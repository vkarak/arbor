#pragma once

#include <cell_group.hpp>
#include <dss_cell_description.hpp>
#include <util/span.hpp>
#include <util/unique_any.hpp>

namespace nest {
namespace mc {

/// Cell_group to collect spike sources
class dss_cell_group: public cell_group {
public:
    dss_cell_group(std::vector<cell_gid_type> gids,
                   const std::vector<util::unique_any>& cell_descriptions):
        gids_(std::move(gids))
    {
        using util::make_span;
        for (cell_gid_type i: make_span(0, cell_descriptions.size())) {
            // store spike times from description
            auto times = util::any_cast<dss_cell_description>(cell_descriptions[i]).spike_times;
            util::sort(times);
            spike_times_.push_back(std::move(times));

            // Take a reference to the first spike time
            not_emit_it_.push_back(spike_times_[i].begin());
        }
    }

    virtual ~dss_cell_group() = default;

    cell_kind get_cell_kind() const override {
        return cell_kind::data_spike_source;
    }

    void reset() override {
        // Reset the pointers to the next undelivered spike to the start
        // of the input range.
        auto it = not_emit_it_.begin();
        auto times = spike_times_.begin();
        for (;it != not_emit_it_.end(); ++it, times++) {
            *it = times->begin();
        }

        clear_spikes();
    }

    void set_binning_policy(binning_kind policy, time_type bin_interval) override
    {}

    void advance(time_type tfinal, time_type dt) override {
        for (auto i: util::make_span(0, not_emit_it_.size())) {
            // The first potential spike_time to emit for this cell
            auto spike_time_it = not_emit_it_[i];

            // Find the first spike past tfinal
            not_emit_it_[i] = std::find_if(
                spike_time_it, spike_times_[i].end(),
                [tfinal](time_type t) {return t >= tfinal; }
            );

            // Loop over the range and create spikes
            for (; spike_time_it != not_emit_it_[i]; ++spike_time_it) {
                spikes_.push_back({ {gids_[i], 0u}, *spike_time_it });
            }
        }
    };

    void enqueue_events(const std::vector<postsynaptic_spike_event>& events) override {
        std::runtime_error("The dss_cells do not support incoming events!");
    }

    const std::vector<spike>& spikes() const override {
        return spikes_;
    }

    void clear_spikes() override {
        spikes_.clear();
    }

    std::vector<probe_record> probes() const override {
        return probes_;
    }

    void add_sampler(cell_member_type probe_id, sampler_function s, time_type start_time = 0) override {
        std::logic_error("The dss_cells do not support sampling of internal state!");
    }

private:
    // Spikes that are generated.
    std::vector<spike> spikes_;

    // Map of local index to gid
    std::vector<cell_gid_type> gids_;

    std::vector<probe_record> probes_;

    // The dss_cell is simple: Put all logic in the cellgroup cause accelerator support
    // is not expected. We need storage for the cell state

    // The times the cells should spike, one for each cell, sorted in time
    std::vector<std::vector<time_type> > spike_times_;

    // Each cell needs its own itterator to the first spike not yet emitted
    std::vector<std::vector<time_type>::iterator > not_emit_it_;
};

} // namespace mc
} // namespace nest
