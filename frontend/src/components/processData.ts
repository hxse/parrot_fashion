import { srtType } from './analyzeSrt'

export type fileAllType = {
  // [_: string]: string | boolean | number[] | null
  author: string
  fileName: string
  filePath: string
  fileSuffix: string
  isFile: boolean
  name: string
  parent: string
  type: string
  idx: number[]
  children: null
  data?: Blob | string | srtType[]
}
type fileAllTypeObj = {
  [_: string]: fileAllType[]
}
type fileAllTypeObj2 = {
  [_: string]: fileAllTypeObj
}
type fileAllTypeObject = {
  [_: string]: fileAllType[] | fileAllTypeObject
}
export type newType = {
  name: string
  children: newType[] | fileAllType[] | null
  idx: number[] | null
}
export type childrenType = newType[] | fileAllType[] | null | undefined

function isFileAllTypeArray(
  obj: fileAllType[] | fileAllTypeObject
): obj is fileAllType[] {
  return obj instanceof Array
}

function getFileId(file: fileAllType) {
  //必须得有个id,才能把mp3和srt放在一起, 取文件名+key
  const trunk = file.fileName.split(' ')
  return (
    trunk.slice(0, trunk.length - 1).join(' ') +
    trunk[trunk.length - 1].split('.')[0]
  )
  return file.fileName.split(' ')[0]
}

function getObj1(data: fileAllType[]): [fileAllTypeObj, string[]] {
  const resArr: string[] = []
  const resObj: fileAllTypeObj = {}
  for (const item of data) {
    if (item.isFile == true) {
      const name: string = item.author + '|' + item.parent
      if (resObj[name] === undefined) {
        resArr.push(name)
      }
      const value = resObj[name]
      resObj[name] = value ? [...value, item] : [item]
    }
  }
  return [resObj, resArr]
}
function getObj2(resObj: fileAllTypeObj, resArr: string[]): fileAllTypeObj2 {
  const resObj2: fileAllTypeObj2 = {}
  for (const name of resArr) {
    const idObj: fileAllTypeObj = {}
    for (const item of resObj[name]) {
      const itemId = getFileId(item)
      const value = idObj[itemId]
      idObj[itemId] = value ? [...value, item] : [item]
    }
    resObj2[name] = idObj
  }
  return resObj2
}

type sortCallbackType = (
  a: string | fileAllType,
  b: string | fileAllType
) => number
const sortCallback: sortCallbackType = (a, b) => {
  if (!(typeof a == 'string') && !(typeof b == 'string')) {
    return a.name > b.name ? 1 : -1
  } else {
    return a > b ? 1 : -1
  }
}
function getObj3(
  name: string,
  children: fileAllTypeObject | fileAllType[],
  sortCallback: sortCallbackType
): newType {
  //todo 重写一次更好的支持类型
  if (isFileAllTypeArray(children)) {
    return {
      name: name,
      children: children
        .sort(sortCallback)
        .map((i) => ({ ...i, children: null, idx: null })),
      idx: null
    }
  }
  const keyArr = Object.keys(children).sort(sortCallback)
  const data: newType[] = keyArr.map((i) => {
    const value = children[i]
    return getObj3(i, value, sortCallback)
  })
  return { name: name, children: data, idx: null }
}
function addIdx(newData: newType, pre: number[] = []) {
  //各文件加一个带目录层级的序号
  if (newData['children'] != undefined) {
    for (const [idx, value] of Object.entries(newData['children'])) {
      value['idx'] = [...pre, parseInt(idx)]
      addIdx(value, [...pre, parseInt(idx)])
    }
  }
}
export function reconstruct(text: string) {
  const data: fileAllType[] = JSON.parse(text)

  const [resObj, resArr] = getObj1(data)

  const resObj2 = getObj2(resObj, resArr)

  //重新整理下数据结构
  const resObj3 = getObj3('.', resObj2, sortCallback)

  addIdx(resObj3)

  return resObj3
}
