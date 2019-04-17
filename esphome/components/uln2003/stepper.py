from esphome import pins
from esphome.components import stepper
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_ID, CONF_PIN_A, CONF_PIN_B, CONF_PIN_C, CONF_PIN_D, \
    CONF_SLEEP_WHEN_DONE, CONF_STEP_MODE


uln2003_ns = cg.esphome_ns.namespace('uln2003')
ULN2003StepMode = uln2003_ns.enum('ULN2003StepMode')

STEP_MODES = {
    'FULL_STEP': ULN2003StepMode.ULN2003_STEP_MODE_FULL_STEP,
    'HALF_STEP': ULN2003StepMode.ULN2003_STEP_MODE_HALF_STEP,
    'WAVE_DRIVE': ULN2003StepMode.ULN2003_STEP_MODE_WAVE_DRIVE,
}

ULN2003 = uln2003_ns.class_('ULN2003', stepper.Stepper, cg.Component)

CONFIG_SCHEMA = stepper.STEPPER_SCHEMA.extend({
    cv.Required(CONF_ID): cv.declare_variable_id(ULN2003),
    cv.Required(CONF_PIN_A): pins.gpio_output_pin_schema,
    cv.Required(CONF_PIN_B): pins.gpio_output_pin_schema,
    cv.Required(CONF_PIN_C): pins.gpio_output_pin_schema,
    cv.Required(CONF_PIN_D): pins.gpio_output_pin_schema,
    cv.Optional(CONF_SLEEP_WHEN_DONE, default=False): cv.boolean,
    cv.Optional(CONF_STEP_MODE, default='FULL_STEP'): cv.one_of(*STEP_MODES, upper=True, space='_')
}).extend(cv.COMPONENT_SCHEMA)


def to_code(config):
    pin_a = yield cg.gpio_pin_expression(config[CONF_PIN_A])
    pin_b = yield cg.gpio_pin_expression(config[CONF_PIN_B])
    pin_c = yield cg.gpio_pin_expression(config[CONF_PIN_C])
    pin_d = yield cg.gpio_pin_expression(config[CONF_PIN_D])
    var = cg.new_Pvariable(config[CONF_ID], pin_a, pin_b, pin_c, pin_d)
    yield cg.register_component(var, config)
    yield stepper.register_stepper(var, config)

    cg.add(var.set_sleep_when_done(config[CONF_SLEEP_WHEN_DONE]))
    cg.add(var.set_step_mode(STEP_MODES[config[CONF_STEP_MODE]]))
