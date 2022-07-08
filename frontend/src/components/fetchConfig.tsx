import { useAtom, atom, Atom, Provider } from 'jotai'
import { urlAtom } from './fetchData'

export const urlAtomConfig = atom<string>((get) => get(urlAtom) + '/config')
export const isLoadingAtom = atom<string>('init')
export const dataAtom = atom<JSON | null>(null)
export const fetchAtom = atom(
  () => undefined,
  async (get, set) => {
    try {
      set(isLoadingAtom, 'waiting...')
      const response = await fetch(get(urlAtomConfig))
      const resData = await response.json()
      set(isLoadingAtom, 'end')
      console.log(resData)
      set(dataAtom, resData)
    } catch (error) {
      console.log(error)
      set(isLoadingAtom, 'error')
    }
  }
)

export const fetchConfigObjAtom = {
  urlAtom: urlAtomConfig,
  isLoadingAtom: isLoadingAtom,
  dataAtom: dataAtom,
  fetchAtom: fetchAtom
}

export const getData = async (url: string): Promise<any> => {
  const response = await fetch(url)
  const resData = await response.json()
  const dataObj = JSON.parse(resData)
  console.log(2333, dataObj)
  return dataObj
}

export const postData = async (url: string, body: object): Promise<any> => {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  })
  const resData = await response.json()
  return resData
}
