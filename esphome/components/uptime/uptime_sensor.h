#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace uptime {

class UptimeSensor : public sensor::PollingSensorComponent {
 public:
  explicit UptimeSensor(const std::string &name, uint32_t update_interval);

  void update() override;

  float get_setup_priority() const override;

  std::string unique_id() override;

 protected:
  uint64_t uptime_{0};
};

}  // namespace uptime
}  // namespace esphome
