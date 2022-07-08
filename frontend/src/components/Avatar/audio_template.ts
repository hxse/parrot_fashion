import { atom, Atom, Getter, Setter } from 'jotai'
import { newType, fileAllType } from './processData'
import { str2srt, srtType } from './analyzeSrt'
import { idxDirAtom, dirObjAtom } from './fetchData'
import { childrenType } from './processData'
import { pathType } from './fetchData'

const audioSuffix: string[] = ['.mp3', '.mp4', '.webm']
const subtitleSuffix: string[] = ['.srt']
const language: string[] = ['.en', '.en-GB', '.en-us', '.ja']
const translate: string[] = ['cn', '.zh-cn', '.zh-CN', '.zh-HK', '.zh-TW']
const translateTag: string[] = ['.ytb', '.autosub']

const temp: string[] = []
const temp2: string[] = []
for (const tag of translateTag) {
  for (const i of language) {
    temp.push(tag + i)
  }
  for (const i of translate) {
    temp2.push(tag + i)
  }
}
language.push(...temp)
translate.push(...temp2)

function checkAudioSuffix(file: fileAllType): boolean {
  return audioSuffix.some((suffix) => file.name.endsWith(suffix))
}
function getStem(name: string): string {
  return name.split('.').slice(0, -1).join('.')
}
function checkFileAllType(
  obj: newType[] | fileAllType[]
): obj is fileAllType[] {
  return obj?.at(-1)?.children === null
}
function tileArray<T>(array: T[][]): T[] {
  return array.reduce((pre, cur) => {
    return pre.concat(cur)
  }, [])
}
function getSubtitleArr(
  stemArr: string[],
  subtitleArr: string[],
  children: fileAllType[]
): fileAllType[][] {
  const resArr: fileAllType[][] = []
  const cacheArr: string[] = []
  for (const stem of stemArr) {
    for (const file of children) {
      for (const subtitle of subtitleArr) {
        for (const suffix of subtitleSuffix) {
          if (stem + subtitle + suffix == file.name) {
            if (cacheArr.indexOf(file.name) == -1) {
              cacheArr.push(file.name)
              resArr.push([file])
            } else {
              resArr.at(-1)?.push(file)
            }
          }
        }
      }
    }
  }
  return resArr
}
function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

type controlType = {
  show: { key?: string; state: boolean }
  play: { key?: string; state: boolean }
}
type cardType = {
  idx: number
  text: { text: string; control: controlType }[]
  audio: {
    startTime: number
    endTime: number
    control: controlType
  }
}
type cardObjType = {
  count: number
  originFile: fileAllType
  targetFile: fileAllType
  audioFile: fileAllType
  cardArr: cardType[]
}
type matchType = [
  boolean,
  string,
  {
    audioFile?: fileAllType
    originFile?: fileAllType
    targetFile?: fileAllType
  }
]
export function match(
  children: childrenType,
  config: audioTempConfigType
): matchType {
  if (!children) return [false, 'children不存在', {}]
  if (!checkFileAllType(children)) return [false, `children类型不是file`, {}]

  const audioFile = children.filter((i) =>
    i.name.endsWith(config.audioSuffix)
  )[0]
  if (audioFile === undefined)
    return [false, `${config.audioSuffix} audio文件不存在`, { audioFile }]

  const originFile = children.filter((i) =>
    i.name.endsWith(config.originSuffix)
  )[0]
  if (originFile === undefined)
    return [
      false,
      `${config.originSuffix} origin文件不存在`,
      { audioFile, originFile }
    ]

  const targetFile = children.filter((i) =>
    i.name.endsWith(config.targetSuffix)
  )[0]
  if (targetFile === undefined)
    return [
      false,
      `${config.targetSuffix} target文件不存在`,
      { audioFile, originFile, targetFile }
    ]

  return [true, 'success', { audioFile, originFile, targetFile }]
}

export async function audioTemp(
  children: childrenType,
  config: audioTempConfigType
) {
  const [state, message, { audioFile, originFile, targetFile }] = match(
    children,
    config
  )
  if (
    state === false ||
    audioFile === undefined ||
    originFile === undefined ||
    targetFile == undefined
  ) {
    console.log(message)
    return
  }

  async function getSrtData(fileObj: fileAllType): Promise<srtType[]> {
    const response = await fetch(
      'http://127.0.0.1:8000/file?path=' + encodeURIComponent(fileObj.filePath)
    )
    const blobData = await response.blob()
    const text = await blobData.text()
    const srtArr = str2srt(text).filter((i) => i.text != '')
    return srtArr
  }
  originFile['data'] = await getSrtData(originFile)
  targetFile['data'] = await getSrtData(targetFile)
  if (originFile['data'].length !== targetFile['data'].length) {
    throw `报错,数量不对等 ${originFile['data'].length} ${targetFile['data'].length}`
    return null
  }

  const cardArr: cardType[] = []
  for (let idx = 0; idx < originFile['data'].length; idx++) {
    const originSrtObj = originFile['data'][idx]
    const targetSrtObj = targetFile['data'][idx]
    const card: cardType = {
      audio: {
        startTime: originSrtObj.startTime,
        endTime: originSrtObj.endTime,
        control: { show: { state: true }, play: { state: true } }
      },
      idx: idx,
      text: [originSrtObj, targetSrtObj].map((i) => ({
        text: i.text,
        control: { show: { state: true }, play: { state: true } }
      }))
    }
    cardArr.push(card)
  }

  const resCardObj: cardObjType = {
    count: cardArr.length,
    originFile: originFile,
    targetFile: targetFile,
    audioFile: audioFile,
    cardArr: cardArr
  }
  console.log(resCardObj)
  await sleep(500)
  return resCardObj
}

export type audioTempConfigType = {
  audioSuffix: string
  originSuffix: string
  targetSuffix: string
  mode: string
  idx: Atom<number>
  name: string
  dirPath: string
  // idxDir: number[] #序号不能保证永远一致, 所以不建议, 建议用dirPath反向推算idxDir
}

export type saveAudioTempConfigType = {
  audioSuffix?: string
  originSuffix?: string
  targetSuffix?: string
  idx?: number
  name?: string
}

type configType = {
  dirObj: pathType
  argObj: audioTempConfigType
}
const isLoadingAtom = atom<string>('init')
const dataAtom = atom<cardObjType | null | undefined>(null)
const setTempAtom = atom(
  () => undefined,
  async (get, set, config: configType) => {
    const { dirObj, argObj } = config
    const children: childrenType = dirObj.at(-1)?.children
    try {
      set(isLoadingAtom, 'waiting...')
      set(dataAtom, null)
      const resData = await audioTemp(children, argObj)
      set(isLoadingAtom, 'end')
      set(dataAtom, resData)
    } catch (error) {
      console.log(error)
      set(isLoadingAtom, 'error')
    }
  }
)

export const audioTempAtomObj = {
  isLoadingAtom,
  dataAtom,
  setTempAtom
}
export type audioTempAtomObjType = typeof audioTempAtomObj
import { PluginsChildrenType } from './pluginsChildren'
export type pluginConfigType = {
  pluginAtom: audioTempAtomObjType
  pluginArgs: audioTempConfigType
  PluginsChildren: PluginsChildrenType
}
