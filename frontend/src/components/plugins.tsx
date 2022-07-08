import { useAtom, atom, Atom, Provider } from 'jotai'
import { dirObjAtom, idxDirAtom, idxFileAtom } from './fetchData'
import { childrenType } from './processData'
import { pathType } from './fetchData'
import { useEffect } from 'react'
import { urlAtomConfig, getData, postData } from './fetchConfig'
import {
  viewPlugin,
  ViewChildren,
  pluginConfigType,
  serverTempConfigType,
  viewChildrenType
} from 'plugin/viewPlugin'
import { pluginArr } from './config'
import { recoverRead } from './recoverRead'
import { matchConfig } from './sync'

export const showAtom = atom(-1)
export function AllPlugin() {
  const [dirObj] = useAtom(dirObjAtom)
  const [show, setShow] = useAtom(showAtom)
  const [url] = useAtom(urlAtomConfig)
  useEffect(() => {
    async function temp() {
      //setShow 就可以了
      const resGetData = await recoverRead<string>({ url, getData, postData })
      const recovder = resGetData['recover']
      if (recovder) {
        // const key = recovder.key
        // const data = resGetData[key]
        // for (const i of data) {
        //   const state = matchConfig(i, recovder, [
        //     'name',
        //     'mode',
        //     'dirPath',
        //     'key'
        //   ])
        //   if (state) {
        //     setShow(recovder)
        //     break
        //   }
        // }
        const i = recovder['showIdx']
        setShow(i)
      }

      // const res = resGetData.data.filter((i) => i.current == true)[0]
      // if (res == undefined) return
      // // const p = pluginArr.filter((i, idx) => i.pluginArgs.name == res.name)[0]
      // const p = pluginArr.filter((i) =>
      //   matchConfig(res, i.pluginArgs, ['name', 'mode'])
      // )[0]
      // if (p === undefined) return
      // const index = pluginArr.indexOf(p)
      // setShow(index)
      // console.log('first')
    }
    if (dirObj) {
      temp()
    }
  }, [dirObj])
  return (
    <div>
      {pluginArr.map((i, idx) => (
        <Plugin key={idx} idx={idx} pluginConfig={i}></Plugin>
      ))}
    </div>
  )
}

function Plugin({
  idx,
  pluginConfig
}: {
  idx: number
  pluginConfig: pluginConfigType
}) {
  const { pluginAtom, pluginArgs, PluginChildren } = pluginConfig
  const [dirObj] = useAtom(dirObjAtom)
  const [idxDir] = useAtom(idxDirAtom)
  const [idxFile, setIdxFile] = useAtom(idxFileAtom)
  //   const [show, setShow] = useState(false)
  const [show, setShow] = useAtom(showAtom)
  if (!dirObj) return <div></div>

  const children: childrenType = dirObj?.at(-1)?.children
  const [state, message, data] = pluginConfig.plugin.match(children, pluginArgs)

  //   idx, pluginAtom, pluginConfig, setIdxFile, update
  return (
    <div>
      {state ? (
        show === idx ? (
          // true === true ? (
          <Provider>
            <PluginChildren
              dirObj={dirObj}
              idxDir={idxDir}
              pluginConfig={pluginConfig}
              callback={() => {
                setIdxFile(null)
              }}
            ></PluginChildren>
          </Provider>
        ) : (
          <div onClick={() => setShow(idx)}>
            {pluginConfig.pluginArgs.originSuffix} {'-->'}{' '}
            {pluginConfig.pluginArgs.targetSuffix}
          </div>
        )
      ) : (
        message
      )}
      <br />
    </div>
  )
}
