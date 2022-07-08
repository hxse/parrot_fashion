import { pluginConfigType, match } from './audio_template'
import { atom, useAtom } from 'jotai'
import { useEffect } from 'react'
import { pathType } from './fetchData'
import { saveAudioTempConfigType } from './audio_template'
import { saveType, readType } from './plugins'
import {
  getData,
  postData,
  fetchConfigObjAtom,
  urlAtomConfig
} from './fetchConfig'
export type PluginsChildrenType = typeof AudioChild

export function AudioChild({
  dirObj,
  idxDir,
  pluginConfig,
  read,
  save,
  callback
}: {
  dirObj: pathType
  idxDir: number[]
  pluginConfig: pluginConfigType
  read: readType
  save: saveType
  callback: () => void
}) {
  const { pluginAtom, pluginArgs } = pluginConfig

  const pluginObj = {
    data: useAtom(pluginAtom.dataAtom)[0],
    setData: useAtom(pluginAtom.dataAtom)[1],
    isLoading: useAtom(pluginAtom.isLoadingAtom)[0],
    setTemp: useAtom(pluginAtom.setTempAtom)[1]
  }
  const [idx, setIdx] = useAtom(pluginArgs.idx)

  pluginArgs['dirPath'] = dirObj.map((i) => i?.name).join('/')

  useEffect(() => {
    pluginObj.setTemp({ dirObj: dirObj, argObj: pluginArgs })
    async function read_() {
      const resGetData = await read({ url: url, getData, postData })
      let idx = 0
      for (const i of resGetData.data) {
        if (
          i['name'] === pluginArgs.name &&
          i['dirPath'] == pluginArgs.dirPath
        ) {
          idx = i['idx']
          break
        }
      }
      setIdx(idx)
      save(pluginArgs, { idx: idx }, { url: url, getData, postData }, dirObj)
    }
    read_()
  }, [dirObj])

  const [url] = useAtom(urlAtomConfig)

  function upOrNext(mode: boolean) {
    const data = pluginObj.data
    if (data !== null && data !== undefined) {
      const count = data['count']
      switch (mode) {
        case true:
          if (idx < count - 1) {
            const newIdx = idx + 1
            setIdx(newIdx)
            save(
              pluginArgs,
              { idx: newIdx },
              { url: url, getData, postData },
              dirObj
            )
          }
          break
        case false:
          if (idx > 0) {
            const newIdx = idx - 1
            setIdx(newIdx)
            save(
              pluginArgs,
              { idx: newIdx },
              { url: url, getData, postData },
              dirObj
            )
          }
          break
      }
    }
  }

  return (
    <div>
      <div>isLoading:{pluginObj.isLoading}</div>
      <div>
        idx:{idx + 1} count:{pluginObj?.data?.count}
      </div>
      <div>
        pluginObj data:
        {pluginObj?.data?.cardArr?.[idx]?.text?.map((i, idx) => (
          <div key={idx}>
            <span>{i.text}</span>
          </div>
        ))}
      </div>
      <br />
      {/* <button className="bg-gray-100 shadow" onClick={pluginObj.up}> */}
      <button
        className="bg-gray-100 shadow"
        onClick={() => {
          upOrNext(false)
        }}
      >
        up
      </button>
      <br />
      {/* <button className="bg-gray-100 shadow" onClick={pluginObj.next}> */}
      <button
        className="bg-gray-100 shadow"
        onClick={() => {
          upOrNext(true)
        }}
      >
        next
      </button>
      <br />
    </div>
  )
}
