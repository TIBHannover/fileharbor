import crypto from 'crypto';

export default {
  methods: {
    keyInObj(key, obj) {
      if (typeof obj !== 'object') return false;
      return Object.prototype.hasOwnProperty.call(obj, key);
    },
    isEqual(x, y) {
      return this.stringify(x) === this.stringify(y);
    },
    stringify(x) {
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
      return JSON.stringify(x);
    },
    isArray(obj) {
      return !!obj && obj.constructor === Array;
    },
    capitalize(str) {
      return str && `${str.charAt(0).toUpperCase()}${str.slice(1)}`;
    },
    getHash(x) {
      const md5 = crypto.createHash('md5');
      const hash = md5.update(JSON.stringify(x));
      return hash.digest('hex').substring(0, 10);
    },
    repPlace(x, y) {
      const string = y.replace(
        /{(\w+)}/g,
        (withDelimiters, withoutDelimiters) => (
          this.keyInObj(withoutDelimiters, x)
            ? x[withoutDelimiters] : withDelimiters),
      );
      return string;
    },
  },
};
