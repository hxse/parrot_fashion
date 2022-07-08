import { viewPlugin, pluginConfigType, serverTempConfigType } from './index'
import { atom, useAtom } from 'jotai'
import { useEffect } from 'react'
import { pathType } from 'components/fetchData'
import {
  readConfig,
  saveConfig,
  matchConfig,
  matchFieldType,
  serverConfigType,
  serverFullConfigType
} from 'components/sync'
import { recoverObjType } from 'components/recoverRead'
import {
  getData,
  postData,
  fetchConfigObjAtom,
  urlAtomConfig
} from 'components/fetchConfig'
import { configsType, serverType } from 'components/config'
import { showAtom } from 'components/plugins'
import { idxDirAtom } from 'components/fetchData'
import { cardType, keyStr, keyType } from './template'
export type viewChildrenType = typeof ViewChildren

function reverse(arr: number[]) {
  const res = []
  for (let idx = arr.length - 1; idx >= 0; idx--) {
    res.push(idx)
  }
  return res
}
function random(arr: number[]) {
  for (let i = 1; i < arr.length; i++) {
    const random = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[random]] = [arr[random], arr[i]]
  }
  return arr
}

export function ViewChildren({
  dirObj,
  idxDir,
  pluginConfig,
  callback
}: {
  dirObj: pathType
  idxDir: number[]
  pluginConfig: pluginConfigType
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
  const [idxArr, setIdxDirChild] = useAtom(pluginArgs.idxDir)

  const [showIdx] = useAtom(showAtom)

  pluginArgs['dirPath'] = dirObj.map((i) => i?.name).join('/')

  const matchField: matchFieldType = ['name', 'dirPath', 'mode']
  useEffect(() => {
    async function read_() {
      const resGetData = await readConfig({
        url: url,
        getData,
        postData
      })
      const obj = {
        key: pluginArgs['key'],
        name: pluginArgs['name'],
        mode: pluginArgs['mode'],
        dirPath: pluginArgs['dirPath'],
        idx: idx,
        idxDir: idxDir,
        showIdx: showIdx
      }
      const key = resGetData['recover']['key']
      if (!key && resGetData['data'].length == 0) {
        resGetData['recover'] = {
          key: pluginArgs['key'],
          keyIdx: 0,
          showIdx: showIdx
        }
        resGetData['data'] = [obj]
        postData(url, resGetData)
        return
      }

      function getMatchIdx(): number | null {
        let idx: number | null = null
        for (const [index, value] of resGetData['data'].entries()) {
          if (matchConfig(value, pluginArgs, matchField)) {
            idx = index
            // newReadConfig = value
            break
          }
        }
        return idx
      }
      let keyIdx = getMatchIdx()
      if (keyIdx == null) {
        resGetData['data'].push(obj)
        resGetData['recover']['key'] = key
        keyIdx = resGetData['data'].length - 1
        resGetData['recover']['keyIdx'] = keyIdx
      } else {
        resGetData['data'][keyIdx] = {
          ...resGetData['data'][keyIdx],
          ...{}
        }
        resGetData['recover']['key'] = key
        resGetData['recover']['keyIdx'] = keyIdx
      }
      postData(url, resGetData)
      setIdx(resGetData['data'][keyIdx]['idx'] ?? 0)
      // saveConfig(
      //   { url: url, getData, postData },
      //   pluginArgs,
      //   {
      //     idx: idx,
      //     idxDir: idxArr
      //     // setIdx: undefined,
      //     // setIdxArr: undefined
      //   },
      //   showIdx,
      //   idxDir
      // )
      return
    }

    if (pluginObj.data) {
      read_()
      console.log('data 存在', pluginObj.data)
    }
  }, [pluginObj.data])

  useEffect(() => {
    pluginObj.setTemp({ dirObj: dirObj, argObj: pluginArgs })
    console.log('data 不存在', pluginObj.data)
  }, [dirObj])

  const [url] = useAtom(urlAtomConfig)

  function upOrNext(mode: boolean) {
    const data = pluginObj.data
    if (data !== null && data !== undefined) {
      const count = data['count']
      switch (mode) {
        case false:
          if (idx > 0) {
            const newIdx = idx - 1
            setIdx(newIdx)
            saveConfig(
              { url: url, getData, postData },
              pluginArgs,
              {
                idx: newIdx,
                idxDir: idxDir
                // setIdx: undefined,
                // setIdxArr: undefined
              },
              showIdx,
              idxDir
            )
          }
          break
        case true:
          if (idx < count - 1) {
            const newIdx = idx + 1
            setIdx(newIdx)
            saveConfig(
              { url: url, getData, postData },
              pluginArgs,
              {
                idx: newIdx,
                idxDir: idxDir
                // setIdx: undefined,
                // setIdxArr: undefined
              },
              showIdx,
              idxDir
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
