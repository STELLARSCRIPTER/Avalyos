namespace AVALYOS.Quantum {
    
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Measurement;

    /// Represents a company branch with geographic and organizational information
    newtype Branch = (
        Code: String,
        Company: String,
        Continent: String,
        Country: String,
        State: String,
        Sector: String,
        SubSector: String,
        Employees: Int
    );

    /// Returns an array of sample branches from the AVALYOS dataset
    function GetSampleBranches() : Branch[] {
        return [
            Branch("ms01", "Microsoft", "Asia", "India", "Telangana", "Technology", "Cloud Computing", 12000),
            Branch("gg01", "Google", "Asia", "India", "Karnataka", "Technology", "Search & Advertising", 18000),
            Branch("jj01", "Johnson & Johnson", "Asia", "India", "Tamil Nadu", "Pharma", "Pharmaceutical Manufacturing", 8000),
            Branch("pf01", "Pfizer", "Asia", "Singapore", "West", "Pharma", "Pharmaceutical Manufacturing", 5500),
            Branch("ty01", "Toyota", "Asia", "Japan", "Tokyo", "Automotive", "Vehicle Manufacturing", 50000),
            Branch("ba01", "BASF", "Asia", "China", "Shanghai", "Pharma", "Chemical Manufacturing", 15000)
        ];
    }

    /// Generates a quantum random integer between 0 and max-1
    /// Uses Hadamard gates and measurement to generate randomness
    operation QuantumRandomInt(max: Int) : Int {
        if max <= 0 {
            return 0;
        }

        // Determine number of qubits needed to represent max
        let numQubits = BitSizeI(max);
        
        // Allocate qubits for random number generation
        use qubits = Qubit[numQubits];
        
        // Apply Hadamard to each qubit to create superposition
        for qubit in qubits {
            H(qubit);
        }
        
        // Measure all qubits and convert to integer
        let measurementResults = MeasureEachZ(qubits);
        let randomValue = ResultArrayAsInt(measurementResults);
        
        // Reset qubits to |0⟩ state before release
        ResetAll(qubits);
        
        // Ensure result is within bounds [0, max)
        return randomValue % max;
    }

    /// Samples a branch using weighted probability based on employee count
    /// Implements quantum Monte Carlo sampling with cumulative distribution
    operation SampleBranchWeighted() : Branch {
        let branches = GetSampleBranches();
        let branchCount = Length(branches);
        
        // Calculate cumulative weights based on employee counts
        mutable cumulativeWeights = [];
        mutable totalEmployees = 0;
        
        for i in 0..branchCount - 1 {
            let branch = branches[i];
            let employees = branch::Employees;
            set totalEmployees = totalEmployees + employees;
            set cumulativeWeights += [totalEmployees];
        }
        
        // Generate quantum random number normalized to [0, totalEmployees)
        let randomValue = QuantumRandomInt(totalEmployees);
        
        // Find branch based on cumulative distribution
        mutable selectedIndex = 0;
       for i in 0..branchCount - 1 {
    if randomValue < cumulativeWeights[i] {
        return branches[i];
    }
}

        
        return branches[selectedIndex];
    }

    /// Entry point: demonstrates quantum branch sampling
    /// Samples a branch and outputs all its information
    @EntryPoint()
    operation RunTest() : Unit {
        Message("========================================");
        Message("AVALYOS Quantum Branch Sampler");
        Message("========================================");
        Message("");
        
        // Sample a random branch using quantum weighting
        let sampledBranch = SampleBranchWeighted();
        
        // Extract branch information using field accessors
        let code = sampledBranch::Code;
        let company = sampledBranch::Company;
        let continent = sampledBranch::Continent;
        let country = sampledBranch::Country;
        let state = sampledBranch::State;
        let sector = sampledBranch::Sector;
        let subSector = sampledBranch::SubSector;
        let employees = sampledBranch::Employees;
        
        // Display results
        Message("📊 Quantum-Sampled Branch Information:");
        Message("========================================");
        Message($"Code: {code}");
        Message($"Company: {company}");
        Message($"Continent: {continent}");
        Message($"Country: {country}");
        Message($"State: {state}");
        Message($"Sector: {sector}");
        Message($"Sub-Sector: {subSector}");
        Message($"Employees: {employees}");
        Message("========================================");
        Message("");
        Message("✓ Quantum sampling completed successfully!");
    }
}
