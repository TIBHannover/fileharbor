import * as jsts from 'jsts';

export function lsplit(x, sep, maxsplit) {
  x = x.split(sep);
  const result = x.splice(0, maxsplit);
  if (x.length) {
    result.push(x.join(sep));
  }
  return result;
}

export function isMobile() {
  const devices = [
    'Android', 'webOS', 'iPhone', 'iPod',
    'BlackBerry', 'IEMobile', 'Opera Mini',
  ];
  const filter = new RegExp(devices.join('|'), 'i');
  if (filter.test(navigator.userAgent)) {
    return true;
  }
  return false;
}

export function vectorToJts(points) {
  return points.map(([x, y]) => new jsts.geom.Coordinate(x, y));
}

export function inflatePolygon(points, spacing) {
  try {
    const input = vectorToJts(points); input.push(input[0]);
    const geometryFactory = new jsts.geom.GeometryFactory();
    let polygon = geometryFactory.createPolygon(input);
    const { BufferParameters } = jsts.operation.buffer;
    polygon = polygon.buffer(spacing, BufferParameters.CAP_FLAT);
    const { _coordinates } = polygon._shell._points;
    return _coordinates.map(({ x, y }) => [x, y]);
  } catch (error) {
    return points;
  }
}

export function getCentroid(points) {
  const input = vectorToJts(points); input.push(input[0]);
  const geometryFactory = new jsts.geom.GeometryFactory();
  const polygon = geometryFactory.createPolygon(input);
  const { _coordinates } = polygon.getCentroid();
  const { x, y } = _coordinates._coordinates[0];
  return [x, y];
}
