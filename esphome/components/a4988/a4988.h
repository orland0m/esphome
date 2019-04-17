#pragma once

#include "esphome/core/component.h"
#include "esphome/core/esphal.h"
#include "esphome/components/stepper/stepper.h"

namespace esphome {
namespace a4988 {

class A4988 : public stepper::Stepper, public Component {
 public:
  A4988(GPIOPin *step_pin, GPIOPin *dir_pin) : step_pin_(step_pin), dir_pin_(dir_pin) {}
  void set_sleep_pin(GPIOPin *sleep_pin) { this->sleep_pin_ = sleep_pin; }
  void setup() override;
  void dump_config() override;
  void loop() override;
  float get_setup_priority() const override { return setup_priority::HARDWARE; }

 protected:
  GPIOPin *step_pin_;
  GPIOPin *dir_pin_;
  GPIOPin *sleep_pin_{nullptr};
  HighFrequencyLoopRequester high_freq_;
};

}  // namespace a4988
}  // namespace esphome
