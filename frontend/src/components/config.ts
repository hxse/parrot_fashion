import { useAtom, atom, Atom, Provider } from 'jotai'
import {
  viewPlugin,
  ViewChildren,
  pluginConfigType,
  pluginConfigType2,
  serverTempConfigType,
  viewChildrenType,
  keyStr,
  keyType
} from 'plugin/viewPlugin'
import { recoverObjType } from './recoverRead'

const idx1 = atom<number>(0)
const setIdx1 = atom(
  (get) => get(idx1),
  (get, set, n: number) => {
    set(idx1, n)
  }
)

const idxArr1 = atom<number[]>([])
const setIdxArr1 = atom(
  (get) => get(idxArr1),
  (get, set, nArr: number[]) => {
    set(idxArr1, nArr)
  }
)
const idx2 = atom<number>(0)
const setIdx2 = atom(
  (get) => get(idx2),
  (get, set, n: number) => {
    set(idx2, n)
  }
)

const idxArr2 = atom<number[]>([])
const setIdxArr2 = atom(
  (get) => get(idxArr2),
  (get, set, nArr: number[]) => {
    set(idxArr2, nArr)
  }
)
type testType = 'test'
const test: testType = 'test'
export type keysType = keyType | testType
// type child<T, K extends keyof T> = {
//   [P in keyof T]: Pick<T[P], 'pluginArgs'>
// }
type getP<T> = {
  [P in keyof T]: T[P]
}
export type configsType = pluginConfigType | pluginConfigType2
export type serverType = configsType[][number]['pluginArgsSave']
export type configFileType = {
  recover: recoverObjType
  data: serverType[]
}
// export const keys: keysType = test
function getConfig(): configsType[] {
  return [
    //#不要idxDir, 原因是序号不能保证是永远一致的
    {
      pluginAtom: viewPlugin.tempAtomObj,
      PluginChildren: ViewChildren,
      plugin: viewPlugin,
      pluginArgs: {
        key: 'view',
        audioSuffix: '.mp3',
        originSuffix: '.en.srt',
        targetSuffix: '.en.autosub.zh-cn.srt',
        name: 'mp3_en_autosub-zh-cn.json',
        mode: 'random',
        dirPath: ''
        // idx: idx1,
        // setIdx: setIdx1,
        // idxArr: idxArr1,
        // setIdxArr: setIdxArr1
      },
      pluginArgsSave: { key: 'view' }
    },
    {
      pluginAtom: viewPlugin.tempAtomObj,
      PluginChildren: ViewChildren,
      plugin: viewPlugin,
      pluginArgs: {
        key: 'view',
        audioSuffix: '.mp3',
        originSuffix: '.ja.srt',
        targetSuffix: '.ja.autosub.zh-cn.srt',
        name: 'mp3_ja_autosub-zh-cn.json',
        mode: 'random',
        dirPath: ''
        // idx: idx2,
        // setIdx: setIdx2,
        // idxArr: idxArr2,
        // setIdxArr: setIdxArr2
      },
      pluginArgsSave: { key: 'view' }
    }
  ].map((i) => {
    const idx1 = atom<number>(0)
    const setIdx1 = atom(
      (get) => get(idx1),
      (get, set, n: number) => {
        set(idx1, n)
      }
    )
    const idxArr1 = atom<number[]>([])
    const setIdxArr1 = atom(
      (get) => get(idxArr1),
      (get, set, nArr: number[]) => {
        set(idxArr1, nArr)
      }
    )
    return {
      ...i,
      pluginArgs: {
        ...i.pluginArgs,
        // idx: idx1,
        // setIdx: setIdx1,
        idx: setIdx1,
        // idxDir: idxArr1,
        // setIdxDir: setIdxArr1
        idxDir: setIdxArr1
      }
    }
  })
}
export const pluginArr = getConfig()
