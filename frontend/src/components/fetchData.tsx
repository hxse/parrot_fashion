import { atom, useAtom, Provider } from 'jotai'
import { reconstruct, newType, fileAllType } from './processData'
import { AllPlugin } from './plugins'
import { Control } from './control'
import { urlAtomConfig, getData, postData } from './fetchConfig'
import { recoverRead } from './recoverRead'
import { useEffect } from 'react'

const mainUrl = 'http://127.0.0.1:8000'
// url = 'https://httpbin.org/delay/5'
export const urlAtom = atom<string>(mainUrl)
export const fileAllUrlAtom = atom<string>((get) => get(urlAtom) + '/file_all')
export const isLoadingAtom = atom<string>('init')
export const dataAtom = atom<newType | null>(null)
export const fetchAtom = atom(
  () => undefined,
  async (get, set) => {
    try {
      set(isLoadingAtom, 'waiting...')
      const response = await fetch(get(fileAllUrlAtom))
      const text = await response.text()
      set(isLoadingAtom, 'end')
      const resData = reconstruct(text)
      console.log(resData)
      set(dataAtom, resData)
    } catch (error) {
      console.log(error)
      set(isLoadingAtom, 'error')
    }
  }
)
export const updateAtom = atom<boolean>(false)
export type pathType = (newType | fileAllType | null)[]
function findFile(
  data: newType[] | fileAllType[],
  idxArr: number[],
  bar: pathType = []
): pathType {
  if (idxArr.length <= 0) return bar
  if (idxArr[0] >= data.length) return bar
  const obj = data[idxArr[0]]
  if (obj.children == null) {
    return bar
  }
  bar.push(obj)
  return findFile(obj.children, idxArr.slice(1), bar)
}
export const idxDirAtom = atom<number[]>([])
export const idxFileAtom = atom<number | null>(null)
export const idxPathAtom = atom<number[]>((get) => {
  const idxFile = get(idxFileAtom)
  return idxFile === null ? [...get(idxDirAtom)] : [...get(idxDirAtom), idxFile]
})
export const dirObjAtom = atom<pathType | null>((get) => {
  const data = get(dataAtom)
  const idxDirArr = get(idxDirAtom)
  if (data === null) return null
  if (data.children === null) return null
  const bar = findFile(data.children, idxDirArr)
  return [data, ...bar]
})
function isFileAllType(obj: newType | fileAllType): obj is fileAllType {
  return obj.children === null
}
function getFile(dir: pathType | null, idx: number | null): fileAllType | null {
  if (idx === null) return null
  if (dir === null) return null
  const children = dir?.at(-1)?.children
  if (children == null) return null
  if (idx >= children.length) return null
  const obj = children[idx]
  if (isFileAllType(obj)) {
    return obj
  }
  return null
}
export const fileObjAtom = atom<fileAllType | null>((get) => {
  return getFile(get(dirObjAtom), get(idxFileAtom))
})
export const pathObjAtom = atom<pathType | null>((get) => {
  const dir = get(dirObjAtom)
  if (dir === null) return null
  const file = get(fileObjAtom)
  if (file === null) return dir
  return [...dir, file]
})

export const mp3SubtitleAtom = atom<string[]>(['.mp3'])
export const enSubtitleAtom = atom<string[]>(['.en.srt', '.en-us.srt'])
export const cnSubtitleAtom = atom<string[]>([
  '.cn.srt',
  '.zh-cn.srt',
  '.zh-CN.srt',
  '.zh-TW.srt',
  '.zh-HK.srt'
])

export default function InputUrl() {
  const [url, setUrl] = useAtom(urlAtom)
  const [fileAllUrl] = useAtom(fileAllUrlAtom)
  const [isLoading] = useAtom(isLoadingAtom)
  const [data] = useAtom(dataAtom)
  const [, fetchData] = useAtom(fetchAtom)

  const [idxDirArr, setIdxDirArr] = useAtom(idxDirAtom)
  const [idxFile, setIdxFile] = useAtom(idxFileAtom)
  const [idxPathArr] = useAtom(idxPathAtom)

  const [dirObj] = useAtom(dirObjAtom)
  const [fileObj] = useAtom(fileObjAtom)
  const [pathObj] = useAtom(pathObjAtom)

  const [update, setUpdateAtom] = useAtom(updateAtom)

  // const audioTempObj = {
  //   data: useAtom(audioTempAtomObj.dataAtom)[0],
  //   isLoading: useAtom(audioTempAtomObj.isLoadingAtom)[0],
  //   setTemp: useAtom(audioTempAtomObj.setTempAtom)[1]
  //   // next: useAtom(audioTempAtomObj.nextAtom)[1],
  //   // up: useAtom(audioTempAtomObj.upAtom)[1]
  //   // nextDir: useAtom(audioTempAtomObj.nextDirAtom)[1],
  //   // upDir: useAtom(audioTempAtomObj.upDirAtom)[1]
  // }
  // for (const [pluginAtom, pluginConfig] of pluginArr) {
  //   const res = {
  //     data: useAtom(pluginAtom.dataAtom)[0],
  //     isLoading: useAtom(pluginAtom.isLoadingAtom)[0],
  //     setTemp: useAtom(pluginAtom.setTempAtom)[1],
  //     next: useAtom(pluginAtom.nextAtom)[1],
  //     up: useAtom(pluginAtom.upAtom)[1],
  //     nextDir: useAtom(pluginAtom.nextDirAtom)[1],
  //     upDir: useAtom(pluginAtom.upDirAtom)[1]
  //   }
  // }

  const [urlConfig] = useAtom(urlAtomConfig)
  async function fetchCallback() {
    await fetchData()
    setIdxDirArr([])
    setIdxFile(null)
  }
  async function recover() {
    const resData = await recoverRead({ url: urlConfig, getData, postData })
    const recovder = resData.recover
    if (recovder) {
      // setIdxDirArr 就可以了
      // const current = resData.data.filter((i) => i.current)[0]
      // if (data && current) {
      //   for (const path of current.dirPath.split('/')) {
      //     if (path == '.') continue
      //     const res = data?.children?.filter((i) => i.name == path)[0]
      //     setIdxDirArr(res == undefined || res.idx == null ? [] : res.idx)
      //   }
      // }
    }
  }
  useEffect(() => {
    fetchCallback()
  }, [])
  useEffect(() => {
    if (dirObj) {
      recover()
    }
  }, [dirObj])
  return (
    <div>
      <label>
        <input
          id="inputUrl"
          defaultValue={url}
          className="bg-gray-100 shadow"
          onChange={(event) => {
            setUrl(event.target.value)
          }}
        />
        <button className="bg-gray-300 shadow" onClick={fetchCallback}>
          fetch
        </button>
        <button className="ml-5 bg-gray-300 shadow" onClick={recover}>
          recover
        </button>
      </label>
      <AllPlugin></AllPlugin>
      <Control></Control>
      <div>
        {/* <br />
        <div>status: {isLoading}</div>
        <br />
        <div>fileAllUrl: {fileAllUrl}</div>
        <br />
        <div>idxDirArr:{idxDirArr}</div>
        <div>idxFile:{idxFile}</div>
        <div>idxPath:{idxPathArr}</div>
        <br />
        <button className="bg-gray-100 shadow" onClick={audioTempObj.up}>
          up
        </button>
        <br />
        <button className="bg-gray-100 shadow" onClick={audioTempObj.next}>
          next
        </button>
        <br />
        <button
          className="bg-gray-100 shadow"
          onClick={() => {
            audioTempObj.upDir(() => {
              setIdxFile(null)
              audioTempObj.setTemp()
            })
          }}
        >
          up dir
        </button>
        <br />
        <button
          className="bg-gray-100 shadow"
          onClick={() => {
            audioTempObj.nextDir(() => {
              setIdxFile(null)
              audioTempObj.setTemp()
            })
          }}
        >
          next dir
        </button>
        <br /> */}

        {/* <br />
        <div>dir name:{dirObj?.at(-1)?.name}</div>
        <br />
        <div>
          audioTempObj isLoading:
          {audioTempObj?.isLoading}
        </div>
        <br />
        <div>
          audioTempObj data:
          {audioTempObj?.data?.cardArr?.[audioTempObj?.data?.idx]?.text?.map(
            (i, idx) => (
              <div key={idx}>
                <span>{i.text}</span>
              </div>
            )
          )}
        </div> */}
        <br />
        {dirObj?.at(-1)?.children?.map((i, idx) => (
          <div
            key={idx}
            onClick={() => {
              // function getSubTitle(
              //   file: fileAllType | null,
              //   subTitleArr: string[]
              // ): boolean {
              //   if (file === null) return false
              //   for (const subTitle of subTitleArr) {
              //     if (file.name.endsWith(subTitle)) return true
              //   }
              //   return false
              // }
              if (isFileAllType(i)) {
                setIdxFile(idx)
              } else {
                setIdxDirArr((i) => [...i, idx])
                // audioTempObj.setTemp() //老参数是 i.children,新的不用填children,直接添配置
                setUpdateAtom((i) => !i)
              }
            }}
          >
            {i.name}
          </div>
        ))}
      </div>
      <br />
      <div>file name:{fileObj?.name}</div>
      <br />
      <div>
        file path:
        {pathObj
          ?.slice(0)
          ?.map((i) => i?.name)
          .join('/')}
      </div>
    </div>
  )
}
