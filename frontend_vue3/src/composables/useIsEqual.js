export default function useIsEqual(x, y) {
  return stringify(x) === stringify(y)
}