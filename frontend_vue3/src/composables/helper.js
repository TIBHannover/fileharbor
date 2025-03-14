// import crypto from 'crypto'

export function useHelper() {
  function keyInObj(key, obj) {
    if (typeof obj !== 'object') return false
    return Object.prototype.hasOwnProperty.call(obj, key)
  }

  function isEqual(x, y) {
    return stringify(x) === stringify(y)
  }
  function stringify(x) {
    // const circularReplacer = () => {
    //   const seen = new WeakSet();
    //   return (key, value) => {
    //     if (typeof value === 'object' && value !== null) {
    //       if (seen.has(value)) {
    //         return;
    //       }
    //       seen.add(value);
    //     }
    //     return value;
    //   };
    // };
    return JSON.stringify(x)
  }

  function isArray(obj) {
    return !!obj && obj.constructor === Array
  }

  function capitalize(str) {
    return str && `${str.charAt(0).toUpperCase()}${str.slice(1)}`
  }
  // getHash(x) {
  //   const md5 = crypto.createHash('md5');
  //   const hash = md5.update(JSON.stringify(x));
  //   return hash.digest('hex').substring(0, 10);
  // },
  function repPlace(x, y) {
    const string = y.replace(/{(\w+)}/g, (withDelimiters, withoutDelimiters) =>
      keyInObj(withoutDelimiters, x) ? x[withoutDelimiters] : withDelimiters,
    )
    return string
  }

  return { keyInObj, isEqual, isArray, capitalize, repPlace }
}
