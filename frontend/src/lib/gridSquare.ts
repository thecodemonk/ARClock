/** Convert a 4- or 6-char Maidenhead grid to the center lat/lon of that square. */
export function gridToLatLon(grid: string): { lat: number; lon: number } | null {
  const g = grid.trim();
  if (!/^[A-Ra-r]{2}\d{2}([A-Xa-x]{2})?$/i.test(g)) return null;

  const upper = g.toUpperCase();
  let lon = (upper.charCodeAt(0) - 65) * 20 - 180;
  let lat = (upper.charCodeAt(1) - 65) * 10 - 90;
  lon += parseInt(upper[2]) * 2;
  lat += parseInt(upper[3]) * 1;

  if (g.length >= 6) {
    const subLon = upper.charCodeAt(4) - 65;
    const subLat = upper.charCodeAt(5) - 65;
    lon += subLon * (2 / 24);
    lat += subLat * (1 / 24);
    // center of subsquare
    lon += 1 / 24;
    lat += 1 / 48;
  } else {
    // center of square
    lon += 1;
    lat += 0.5;
  }

  return { lat: parseFloat(lat.toFixed(4)), lon: parseFloat(lon.toFixed(4)) };
}

export function latLonToGrid(lat: number, lon: number): string {
  const adjLon = lon + 180;
  const adjLat = lat + 90;

  const fieldLon = Math.floor(adjLon / 20);
  const fieldLat = Math.floor(adjLat / 10);
  const squareLon = Math.floor((adjLon % 20) / 2);
  const squareLat = Math.floor((adjLat % 10) / 1);
  const subLon = Math.floor(((adjLon % 20) % 2) / (2 / 24));
  const subLat = Math.floor(((adjLat % 10) % 1) / (1 / 24));

  return (
    String.fromCharCode(65 + fieldLon) +
    String.fromCharCode(65 + fieldLat) +
    squareLon.toString() +
    squareLat.toString() +
    String.fromCharCode(97 + subLon) +
    String.fromCharCode(97 + subLat)
  );
}
