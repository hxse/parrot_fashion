import { atom } from 'jotai'
import { idxDirAtom } from './fetchData'
import { showAtom } from './plugins'
import { keysType } from './config'
// export const recoverObjAtom = {
//   idxDir: idxDirAtom,
//   show: showAtom,
//   key: keyAtom
// }
import { keyStr, keyType } from 'plugin/viewPlugin'
function check<K>(obj: any, key: any): obj is K {
  return obj == key
}
const res = check<keyType>('', 'view')
export type recoverObjType = {
  key: string //真的做不到从静态分析中确认是哪个key,除非用泛型赋值
  keyIdx: number
  showIdx: number
  name?: string
  mode?: string
  dirPath?: string
  idxDir?: number[]
}
export type recoverType = {
  [_: string]: any
  recover?: recoverObjType
}
export type fetchType<T> = {
  url: string
  getData: (url: string) => Promise<recoverType>
  postData: (url: string, body: object) => Promise<recoverType>
}
// export type recoverReadType<T> = (
//   fetchObj: fetchType<T>
// ) => Promise<recoverType<T>>

export async function recoverRead<T>({
  url,
  getData,
  postData
}: fetchType<T>): Promise<recoverType> {
  const res = await getData(url)
  console.log(res)
  return res
}
// export const recoverRead: recoverReadType<T> = async ({
//   url,
//   getData,
//   postData
// }) => {
//   const res = await getData(url)
//   console.log(res)
//   return res
// }
