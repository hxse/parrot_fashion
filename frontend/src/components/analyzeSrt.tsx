type tempType = {
  index: number
  key: number
  srtTime: string
}
export type srtType = {
  index: number
  key: number
  srtTime: string
  startTime: number
  endTime: number
  text: string
}
export function str2srt(content: string): srtType[] {
  const reg = new RegExp(/ --> /)

  const contentArr = content
    .split('\n')
    .map((i) => i.trim())
    .filter((i) => i != '')

  const temp: tempType[] = contentArr
    .map((i, index) => ({
      index: index - 1,
      key: parseInt(contentArr[index - 1]),
      srtTime: i
    }))
    .filter((i) => reg.test(i.srtTime))

  const resArr: srtType[] = []
  for (let index = 1; index < temp.length; index++) {
    const el = temp[index]
    const lastEl = temp[index - 1]

    const lastTime = lastEl.srtTime
      .split(' --> ')
      .map((i) => strToTime(i.trim()))
    const lastStartTime = lastTime[0]
    const lastEndTime = lastTime[1]
    if (lastStartTime == undefined || lastEndTime == undefined) {
      throw new Error('无法解析时间')
    }
    const lastEl2: srtType = {
      ...lastEl,
      startTime: lastStartTime,
      endTime: lastEndTime,
      text: ''
    }

    const time = el.srtTime.split(' --> ').map((i) => strToTime(i.trim()))
    const startTime = time[0]
    const endTime = time[1]
    if (startTime == undefined || endTime == undefined) {
      throw new Error('无法解析时间')
    }
    const el2: srtType = {
      ...el,
      startTime: startTime,
      endTime: endTime,
      text: ''
    }

    if (el2.index - lastEl2.index <= 2) {
      resArr.push(lastEl2)
    } else {
      resArr.push({
        ...lastEl2,
        text: contentArr.slice(lastEl2.index + 2, el2.index).join('\n')
      })
    }
    if (index == temp.length - 1) {
      resArr.push({
        ...el2,
        text: contentArr[el2.index + 2] ? contentArr[el2.index + 2] : ''
      })
    }
  }
  return resArr
}

export function strToTime(time: string): number | undefined {
  const len = time.split(':')
  if (len.length == 3) {
    const hour = parseInt(time.split(':')[0])
    const min = parseInt(time.split(':')[1])
    const sec = parseInt(time.split(':')[2].split(',')[0])
    const msec = parseInt(time.split(':')[2].split(',')[1])
    return (
      Number(hour * 3600) + Number(min * 60) + Number(sec) + Number(`0.${msec}`)
    )
  }
}
