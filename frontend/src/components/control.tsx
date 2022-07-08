import { useAtom, atom, Getter, Setter } from 'jotai'
import { dirObjAtom, idxDirAtom, updateAtom, idxFileAtom } from './fetchData'
import { childrenType } from './processData'

function switchDir(
  get: Getter,
  set: Setter,
  callback: () => void,
  mode: boolean
) {
  const children: childrenType = get(dirObjAtom)?.at(-2)?.children
  const idxDirArr = get(idxDirAtom)
  const idxDir = idxDirArr.at(-1)
  if ((children != null || children != undefined) && idxDir != undefined) {
    const count = children.length
    const idx = mode ? idxDir + 1 : idxDir - 1
    if (idx >= 0 && idx < count) {
      set(idxDirAtom, [...idxDirArr.slice(0, idxDirArr.length - 1), idx])
      callback()
    }
  }
}
function parentDir(get: Getter, set: Setter) {
  set(idxDirAtom, (i) => [...i.slice(0, i.length - 1)])
}
const upDirAtom = atom(
  () => undefined,
  async (get, set, callback: () => void) => {
    switchDir(get, set, callback, false)
  }
)

const nextDirAtom = atom(
  () => undefined,
  async (get, set, callback: () => void) => {
    switchDir(get, set, callback, true)
  }
)
const parentDirAtom = atom(() => undefined, parentDir)
export function Control() {
  const [, setUpDir] = useAtom(upDirAtom)
  const [, setNextDir] = useAtom(nextDirAtom)
  const [, setParentDirAtom] = useAtom(parentDirAtom)
  return (
    <div>
      <button
        className="bg-gray-100 shadow"
        onClick={() => {
          setUpDir(() => {
            // setIdxFile(null)
          })
        }}
      >
        up dir
      </button>
      <br />
      <button
        className="bg-gray-100 shadow"
        onClick={() => {
          setNextDir(() => {
            // setIdxFile(null)
          })
        }}
      >
        next dir
      </button>
      <br />
      <button
        className="bg-gray-100 shadow"
        onClick={() => {
          setParentDirAtom()
        }}
      >
        up click
      </button>
    </div>
  )
}
