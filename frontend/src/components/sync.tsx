import {
  viewPlugin,
  ViewChildren,
  pluginConfigType,
  serverTempConfigType,
  viewChildrenType,
  updateType,
  updateServerType,
  keyType
  // keyStr,
  // keyType
} from 'plugin/viewPlugin'
import { pathType } from 'components/fetchData'

export type serverConfigType = serverTempConfigType

export type matchObjType = {
  key: string
  name: string
  dirPath: string
  mode: string
}
export type matchFieldType = ('key' | 'name' | 'dirPath' | 'mode')[]
export function matchConfig(
  obj: any, //serverConfigType,
  pluginArgs: any, //configType,
  field: string[] //matchFieldType
): boolean {
  if (field.length == 0) return false
  return field.every((i) => obj[i] === pluginArgs[i])
}

import {
  recoverType,
  recoverObjType,
  recoverRead
} from 'components/recoverRead'
import { match } from 'assert'
import { postData } from './fetchConfig'
import { numericLiteral } from '@babel/types'
import { configFileType, serverType } from './config'
export type childRecoverObjType = Omit<recoverObjType, 'key'> & {
  key: string
}
export type configType = pluginConfigType['pluginArgs']

export type serverFullConfigType = {
  [_: string]: any
  view: serverTempConfigType[]
  recover?: childRecoverObjType
}
export type fetchObjType<T> = {
  url: string
  getData: (url: string) => Promise<T>
  postData: (url: string, body: T) => Promise<T>
}
// export type readType = (fetchObj: fetchObjType) => Promise<serverFullConfigType>
// export const read: readType = async function ({ url, getData, postData }) {
//   const resGetData = await getData(url)
//   const newObj: serverFullConfigType = {
//     recover: resGetData['recover'],
//     view: resGetData['view'] ?? []
//   }
//   return newObj
// }
export async function readConfig({
  url,
  getData,
  postData
}: fetchObjType<configFileType>): Promise<configFileType> {
  const resGetData = await getData(url)
  const newObj: configFileType = {
    recover: resGetData['recover'] ?? {},
    data: resGetData['data'] ?? []
  }
  return newObj
}
// export type saveConfigType = <K>(
//   fetchObj: fetchObjType<T>,
//   // config: serverFullConfigType,
//   pluginArgs: pluginConfigType['pluginArgs'],
//   update: updateServerType,
//   // recoverObj?: childRecoverObjType
//   idxDir: number[],
//   key: K
// ) => void

export function getKeys<O>(obj: O): Array<keyof O> {
  return Object.keys(obj) as Array<keyof O>
}
type pushDefine = {
  data: { [_: string]: any[] } //泛型约束里的any不可避免,因为只有你不知道才要写约束,全知道了还写啥,因为不知道所以就得写any
  recover: recoverObjType
}

export async function saveConfig(
  { url, getData, postData }: fetchObjType<configFileType>,
  pluginArgs: { key: string; name: string; mode: string; dirPath: string },
  update: updateServerType,
  showIdx: number,
  idxDir: number[]
  // key: string
) {
  const readData = await readConfig({ url: url, getData, postData })
  const key = readData['recover']['key']
  const keyIdx = readData['recover']['keyIdx']
  readData['data'][keyIdx] = { ...readData['data'][keyIdx], ...update }
  const result = await postData(url, readData)
  return result
  // const matchObj: matchObjType = {
  //   key: pluginArgs.key,
  //   name: pluginArgs.name,
  //   mode: pluginArgs.mode,
  //   dirPath: pluginArgs.dirPath
  // }
  // const recover: recoverObjType = {
  //   ...matchObj,
  //   showIdx: showIdx,
  //   idxDir: idxDir
  // }

  const dataArr = readData['data'][pluginArgs.key]
  if (!dataArr) {
    // readData['recover'] = recover
    readData['data'][pluginArgs.key] = []
    const res = await postData(url, readData)
    return
  }
  // readData['recover'] = recover

  let state = true
  for (const [idx, value] of dataArr.entries()) {
    if (matchConfig(value, pluginArgs, ['name', 'mode', 'dirPath', 'key'])) {
      // const newConfig = { ...value, ...matchObj ...update }
      const newConfig = { ...value, ...update }
      dataArr[idx] = newConfig
      state = false
      break
    }
  }
  if (state) {
    // const newConfig = { ...matchObj, ...update }
    const newConfig = { ...update }
    dataArr.push(newConfig)
  }
  const res = await postData(url, readData)
  return res
}
// export const saveConfig: saveConfigType = async (
//   { url, getData, postData },
//   // config,
//   pluginArgs,
//   update,
//   // recoverObj
//   idxDir,
//   key
// ) => {
//   const readData = await read({ url: url, getData, postData })
//   // if (readData.recover) {
//   // if (recoverObj) {
//   const matchObj: matchObjType = {
//     key: keyStr,
//     name: pluginArgs.name,
//     mode: pluginArgs.mode,
//     dirPath: pluginArgs.dirPath
//   }
//   const recover: childRecoverObjType = {
//     ...matchObj,
//     idxDir: idxDir
//   }
//   let state = true
//   for (const [idx, value] of readData[keyStr].entries()) {
//     if (matchConfig(value, pluginArgs, ['name', 'mode', 'dirPath'])) {
//       const newConfig: serverTempConfigType = { ...matchObj, ...update }
//       readData[keyStr][idx] = newConfig
//       state = false
//       break
//     }
//   }
//   if (state) {
//     const newConfig: serverTempConfigType = { ...matchObj, ...update }
//     readData[keyStr].push(newConfig)
//   } else {
//     console.log('不匹配')
//   }
//   const newData: serverFullConfigType = {
//     ...readData,
//     recover
//   }
//   const res = await postData(url, newData)
//   return res
//   // }
//   // }
// }

export type saveType = (
  config: configType,
  update: serverConfigType,
  deleteArr: (keyof configType)[],
  fetchObj: fetchObjType,
  matchField: matchFieldType, //如果为空数组[],那么直接追加一个新的
  dirObj: pathType
) => Promise<void>
function isPluginArgsSave(
  obj: any,
  config: any,
  update: any
): obj is serverConfigType {
  let res = true
  for (const key in obj) {
    console.log(key, obj[key])
    if (
      typeof obj[key]?.read === 'function' &&
      typeof obj[key]?.write === 'function' &&
      typeof obj[key]?.toString === 'function'
    ) {
      res = false
      break
    }
  }
  return res
}
export const save: saveType = async function (
  config,
  update,
  deleteArr,
  { url, getData, postData },
  matchField,
  dirObj
) {
  const newConfig = {
    ...config,
    ...update,
    current: true
  }
  for (const i of deleteArr) {
    delete newConfig[i]
  }
  if (!isPluginArgsSave(newConfig, config, update)) {
    throw `类型要匹配 ${newConfig}`
  }

  const resGetData = await getData(url)
  const dataArr = resGetData[config.key]
  function getType(obj: any): obj is string {
    if (obj) return true
    return false
  }
  resGetData[config.key] = resGetData[config.key] ?? []
  resGetData[config.key]?.forEach((data) => {
    data['current'] = false
  })
  let state = false
  for (const [idx, data] of resGetData[config.key].entries()) {
    if (
      matchConfig(data, config, matchField)
      // data['name'] == newConfig['name'] &&
      // data['dirPath'] == newConfig['dirPath']
    ) {
      resGetData[config.key][idx] = newConfig
      state = true
      break
    }
  }
  if (state == false) {
    resGetData[config.key].push(newConfig)
  }
  const resPostData = await postData(url, {
    ...resGetData,
    [config.key]: resGetData[config.key]
  })
  console.log(resPostData)
}
