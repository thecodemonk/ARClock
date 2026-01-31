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
