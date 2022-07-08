export const obj = { 0: 123, hhh: 456 }
type testType = { a: string; b: string }
const test: testType = { a: '', b: '' }
type aType = { a: string }
const aObj: aType = { a: '123' }
type bType = { b: string }
const bObj: bType = { b: '456' }
type cType = { c: string }
const cObj = { c: '789' }
type arrType = testType[]
const arr = [{ a: '1234', b: '456' }]
// type keyType = 'obj'
const keyStr = 'obj'
type obj2Type = { obj: arrType; haha: { c: string } }
const obj2 = { obj: arr, haha: { c: 'sfd' } }
function getValue<V, K extends keyof V>(o: V, k: K): V[K] {
  return o[k]
}

function getValue2<V, K>(
  o: V,
  k: string | number | symbol
): K extends keyof V ? V[K] : undefined {
  return o[k]
}
getValue(obj, 0)
getValue(obj, 1)
getValue2(obj, 0)
getValue2(obj, 1)

// function getTest<V, K>(a: V, b: K): V & K {
//   //   return Object.assign(a, b)
//   return { ...a, ...b }
// }
// getTest(aObj, bObj)

function post<T>(data: T) {
  return data
}
function getTest<V, K>(a: V, b: K): V & K {
  //   return Object.assign(a, b)
  const v = { ...a, ...b }
  const ha = post(v)
  return v
}
getTest(aObj, { b: '456' })

function demo<V, K>(arr: V[], obj: V): V[] {
  const newRes = { ...arr[0], ...obj }
  const data: testType = { a: '234', b: '234' }
  arr[0] = { ...arr[0], ...obj }
  return arr
}

demo<testType, cType>(arr, { a: '', b: 'sdf' })

function getObj2<V, K extends keyof V>(obj2: V, key: K) {
  return obj2[key]
}
const keyStr2 = 'haha'
const keyStr3 = 'h'
const res = obj2[keyStr]
const res_ = getObj2(obj2, keyStr)
const res2 = getObj2(obj2, keyStr2)
const res3 = getObj2(obj2, keyStr3)

type viewType = 'view'
const view = 'view'
const birdType = 'bird'
const bird = 'bidr'
const keyArr = [view, bird]
for (const i of keyArr) {
  if (i == bird) {
    type resType = typeof i
  }
}
