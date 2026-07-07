// Minimal no-op stubs for class-validator, see @nestjs/common stub for why.
const noopDecorator = () => (_target, _key) => {};
export const IsArray = noopDecorator;
export const IsBoolean = noopDecorator;
export const IsOptional = noopDecorator;
export const IsString = noopDecorator;
