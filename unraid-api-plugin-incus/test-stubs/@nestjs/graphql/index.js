// Minimal no-op stubs for @nestjs/graphql, see @nestjs/common stub for why.
export function ObjectType() {
  return (target) => target;
}
export function InputType() {
  return (target) => target;
}
export function Field() {
  return (_target, _key) => {};
}
