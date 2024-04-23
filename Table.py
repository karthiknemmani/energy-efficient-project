import pandas as pd
from CacheSimulator import CacheSim

def run_sims(filename, associativity):
    total_time = 0.0
    total_energy = 0.0
    
    l1i_accesses = 0.0
    l1i_misses = 0.0
    l1i_hit_rate = 0.0
    l1i_idle_energy = 0.0
    l1i_active_energy = 0.0
    l1i_energy = 0.0
    
    l1d_accesses = 0.0
    l1d_misses = 0.0
    l1d_hit_rate = 0.0
    l1d_idle_energy = 0.0
    l1d_active_energy = 0.0
    l1d_energy = 0.0
    
    l2_accesses = 0.0
    l2_misses = 0.0
    l2_hit_rate = 0.0
    l2_idle_energy = 0.0
    l2_active_energy = 0.0
    l2_energy = 0.0
    
    dram_accesses = 0.0
    dram_idle_energy = 0.0
    dram_active_energy = 0.0
    dram_energy = 0.0
    
    # Run the simulation
    for _ in range(10):
        simulator = CacheSim("./Traces/Spec_Benchmark/" + filename, associativity)
        simulator.run()
        
        total_time += simulator.total_time()
        total_energy += simulator.total_energy()
        l1i_accesses += simulator.l1_instruction.get_accesses()
        l1i_misses += simulator.l1_instruction.get_misses()
        l1i_idle_energy += simulator.l1_instruction.idle_energy()
        l1i_active_energy += simulator.l1_instruction.active_energy()
        l1i_energy += simulator.l1_instruction.active_energy() + simulator.l1_instruction.idle_energy()
        l1d_accesses += simulator.l1_data.get_accesses()
        l1d_misses += simulator.l1_data.get_misses()
        l1d_idle_energy += simulator.l1_instruction.idle_energy()
        l1d_active_energy += simulator.l1_instruction.active_energy()
        l1d_energy += simulator.l1_data.active_energy() + simulator.l1_data.idle_energy()
        l2_accesses += simulator.l2.get_accesses()
        l2_misses += simulator.l2.get_misses()
        l2_idle_energy += simulator.l2.idle_energy()
        l2_active_energy += simulator.l2.active_energy()
        l2_energy += simulator.l2.active_energy() + simulator.l2.idle_energy()
        dram_accesses += simulator.dram.get_accesses()
        dram_idle_energy += simulator.dram.idle_energy()
        dram_active_energy += simulator.dram.active_energy()
        dram_energy += simulator.dram.active_energy() + simulator.dram.idle_energy()
    
    # Compute averages
    l1i_hit_rate = ((l1i_accesses - l1i_misses) / l1i_accesses) if l1i_accesses > 0 else 0
    l1d_hit_rate = ((l1d_accesses - l1d_misses) / l1d_accesses) if l1d_accesses > 0 else 0
    l2_hit_rate = ((l2_accesses - l2_misses) / l2_accesses) if l2_accesses > 0 else 0
    
    l1i_mean_energy = l1i_energy / 10
    l1d_mean_energy = l1d_energy / 10
    l2_mean_energy = l2_energy / 10
    dram_mean_energy = dram_energy / 10

    mean_time = total_time / 10
    mean_energy = total_energy / 10
    
    # Append results to the DataFrame
    row = {
        "File Name": filename,
        "Set Associativity": associativity,
        "Total Access Time (s)": total_time,
        "Mean Time (s)": mean_time,
        "Total Energy (J)": total_energy,
        "Mean Energy (J)": mean_energy,
        "L1i Accesses": l1i_accesses, "L1i Misses": l1i_misses, "L1i Hit Rate": l1i_hit_rate,
        "L1i Idle Consumption (J)": l1i_idle_energy, "L1i Active Consumption (J)": l1i_active_energy, "L1i Energy (J)": l1i_energy, "L1i Mean Energy (J)": l1i_mean_energy,
        "L1d Accesses": l1d_accesses, "L1d Misses": l1d_misses, "L1d Hit Rate": l1d_hit_rate,
        "L1d Idle Consumption (J)": l1d_idle_energy, "L1d Active Consumption (J)": l1d_active_energy, "L1d Energy (J)": l1d_energy, "L1d Mean Energy (J)": l1d_mean_energy,
        "L2 Accesses": l2_accesses, "L2 Misses": l2_misses, "L2 Hit Rate": l2_hit_rate,
        "L2 Idle Consumption (J)": l2_idle_energy, "L2 Active Consumption (J)": l2_active_energy, "L2 Energy (J)": l2_energy, "L2 Mean Energy (J)": l2_mean_energy,
        "DRAM Accesses": dram_accesses, "DRAM Idle Consumption (J)": dram_idle_energy, "DRAM Active Consumption (J)": dram_active_energy, "DRAM Energy (J)": dram_energy, "DRAM Mean Energy (J)": dram_mean_energy
    }
    
    return pd.DataFrame([row])

def main():
    files=[
        "008.espresso.din",
        "013.spice2g6.din",
        "015.doduc.din",
        "022.li.din",
        "023.eqntott.din",
        "026.compress.din",
        "034.mdljdp2.din",
        "039.wave5.din",
        "047.tomcatv.din",
        "048.ora.din",
        "085.gcc.din",
        "089.su2cor.din",
        "090.hydro2d.din",
        "093.nasa7.din",
        "094.fpppp.din"
    ]
    
    associativities = [2, 4, 8]
    
    results = []

    for file in files:
        for num in associativities:
            print("Running simulation for {} with set associativity {}".format(file, num))
            row = run_sims(file, num)
            results.append(row)

    df = pd.concat(results, ignore_index=True)
    
    df.to_csv("simulation_results.csv", index=False)
    
    print("All files processed!")
    
if __name__ == "__main__":
    main()
