# This script was generated by OpenMM-MDL Setup on 2022-11-15.


#	    ,-----.    .-------.     .-''-.  ,---.   .--.,---.    ,---.,---.    ,---. ______       .---.      
#	 .'  .-,  '.  \  _(`)_ \  .'_ _   \ |    \  |  ||    \  /    ||    \  /    ||    _ `''.   | ,_|      
#	 / ,-.|  \ _ \ | (_ o._)| / ( ` )   '|  ,  \ |  ||  ,  \/  ,  ||  ,  \/  ,  || _ | ) _  \,-./  )      
#	;  \  '_ /  | :|  (_,_) /. (_ o _)  ||  |\_ \|  ||  |\_   /|  ||  |\_   /|  ||( ''_'  ) |\  '_ '`)    
#	|  _`,/ \ _/  ||   '-.-' |  (_,_)___||  _( )_\  ||  _( )_/ |  ||  _( )_/ |  || . (_) `. | > (_)  )    
#	: (  '\_/ \   ;|   |     '  \   .---.| (_ o _)  || (_ o _) |  || (_ o _) |  ||(_    ._) '(  .  .-'    
#	 \ `"/  \  ) / |   |      \  `-'    /|  (_,_)\  ||  (_,_)  |  ||  (_,_)  |  ||  (_.\.' /  `-'`-'|___  
#	  '. \_/``".'  /   )       \       / |  |    |  ||  |      |  ||  |      |  ||       .'    |        \ 
#	    '-----'    `---'        `'-..-'  '--'    '--''--'      '--''--'      '--''-----'`      `--------` 
                                                                                                      



from forcefield_water import water_selection, ff_selection, generate_forcefield, water_model_save, generate_transitional_forcefield
from protein_ligand_prep import prepare_protein, protein_choice, prepare_ligand, rdkit_to_openmm, merge_protein_and_ligand
from post_md_conversions import mdtraj_conversion, MDanalysis_conversion
from cleaning_procedures import cleanup, post_md_file_movement 

import simtk.openmm.app as app
from simtk.openmm.app import PDBFile, Modeller, PDBReporter, StateDataReporter, DCDReporter, CheckpointReporter
from simtk.openmm import unit, Platform, Platform_getPlatformByName, MonteCarloBarostat, LangevinMiddleIntegrator
from simtk.openmm import Vec3
import simtk.openmm as mm
import sys
import os
import shutil

# Input Files
############# Ligand and Protein Data ###################
########   Add the Ligand SDf File and Protein PDB File in the Folder with the Script  ######### 

ligand_select = "yes"
ligand_name = "UNK"
ligand_sdf = "6b73_lig.sdf"

minimize = False 
protein = "6b73-processed-processed_openMMDL.pdb"

############# Ligand and Protein Preparation ###################

protein_prepared = "Yes"

############# Forcefield, Water and Membrane Model Selection ###################

ff = 'AMBER14'
water = 'TIP3P-FB'

############# Membrane Settings ###################

add_membrane = True
membrane_lipid_type = 'POPC'
membrane_padding = 1.0
membrane_ionicstrength = 0.0
membrane_positive_ion = 'Na+'
membrane_negative_ion = 'Cl-'

############# Post MD Processing ###################

MDAnalysis_Postprocessing = True
MDTraj_Cleanup = True

# System Configuration

nonbondedMethod = app.PME
nonbondedCutoff = 1.0*unit.nanometers
ewaldErrorTolerance = 0.0005
constraints = app.HBonds
rigidWater = True
constraintTolerance = 0.000001
hydrogenMass = 1.5*unit.amu

# Integration Options

dt = 0.004*unit.picoseconds
temperature = 300*unit.kelvin
friction = 1.0/unit.picosecond
pressure = 1.0*unit.atmospheres
barostatInterval = 25

# Simulation Options

steps = 1000000
equilibrationSteps = 1000
platform = Platform.getPlatformByName('CUDA')
platformProperties = {'Precision': 'single'}
dcdReporter = DCDReporter('trajectory.dcd', 10000)
dataReporter = StateDataReporter('log.txt', 1000, totalSteps=steps,
    step=True, speed=True, progress=True, potentialEnergy=True, temperature=True, separator='\t')
checkpointReporter = CheckpointReporter('checkpoint.chk', 10000)
checkpointReporter2 = CheckpointReporter('10x_checkpoint.chk', 100000)
checkpointReporter3 = CheckpointReporter('100x_checkpoint.chk', 1000000)


if ligand_select == 'yes':
    
    print("Preparing MD Simulation with ligand")
    
    ligand_prepared = prepare_ligand(ligand_sdf,minimize_molecule=minimize)
    
    ligand_prepared
    
    omm_ligand = rdkit_to_openmm(ligand_prepared, ligand_name)
    

        
        

protein_pdb = protein_choice(protein_pre=protein_prepared,protein=protein)
forcefield_selected = ff_selection(ff)
water_selected =water_selection(water=water,force_selection=ff_selection(ff))
model_water = water_model_save(water=water,force_selection=ff_selection(ff))
print("Forcefield and Water Model Selected")
    


if ligand_select == 'yes':
    
    if add_membrane == True:
        transitional_forcefield = generate_transitional_forcefield(protein_ff=forcefield_selected, solvent_ff=water_selected, add_membrane=add_membrane, rdkit_mol=ligand_prepared)
    
    forcefield = generate_forcefield(protein_ff=forcefield_selected, solvent_ff=water_selected, add_membrane=add_membrane, rdkit_mol=ligand_prepared)
    
    complex_topology, complex_positions = merge_protein_and_ligand(protein_pdb, omm_ligand)
    
    print("Complex topology has", complex_topology.getNumAtoms(), "atoms.")    
        

        
modeller = app.Modeller(complex_topology, complex_positions)
 
 
with open(f'prepared_no_solvent_{protein}', 'w') as outfile:
    PDBFile.writeFile(modeller.topology, modeller.positions, outfile)


if add_membrane == True:
    if ff == 'CHARMM36':
        protein_pdb.addMembrane(lipidType= membrane_lipid_type, minimumPadding= membrane_padding * unit.nanometer, positiveIon=membrane_positive_ion, negativeIon=membrane_negative_ion, ionicStrength=membrane_ionicstrength * unit.molar)
        modeller = app.Modeller(protein_pdb.topology, protein_pdb.positions)

    else:
        if model_water == 'charmm' or model_water == 'implicit' or model_water == 'explicit':
            modeller.addMembrane(forcefield, lipidType= membrane_lipid_type, minimumPadding= membrane_padding * unit.nanometer, positiveIon=membrane_positive_ion, negativeIon=membrane_negative_ion, ionicStrength=membrane_ionicstrength * unit.molar)
        else:
            if model_water == 'tip4pew' or model_water == 'tip5p':
                modeller.addMembrane(transitional_forcefield, lipidType= membrane_lipid_type, minimumPadding= membrane_padding * unit.nanometer, positiveIon=membrane_positive_ion, negativeIon=membrane_negative_ion, ionicStrength=membrane_ionicstrength * unit.molar)
            else:
                modeller.addMembrane(forcefield, lipidType= membrane_lipid_type, minimumPadding= membrane_padding * unit.nanometer, positiveIon=membrane_positive_ion, negativeIon=membrane_negative_ion, ionicStrength=membrane_ionicstrength * unit.molar)
    print(f"Protein with Membrane {membrane_lipid_type} prepared")

elif add_membrane == False:
    if Water_Box == "Buffer":
        if model_water == 'charmm' or model_water == 'explicit' or model_water == 'tip3pfb' or model_water == 'tip3':
            modeller.addSolvent(forcefield, padding=water_padding_distance * unit.nanometers, positiveIon=water_positive_ion, negativeIon=water_negative_ion, ionicStrength=water_ionicstrength * unit.molar)
        elif model_water == 'implicit' or model_water == 'charmm_tip4pew':
            protein_pdb.addSolvent(padding=water_padding_distance * unit.nanometers, positiveIon=water_positive_ion, negativeIon=water_negative_ion, ionicStrength=water_ionicstrength * unit.molar)
        else:
            if model_water == 'tip4pfb':
                model_water = 'tip4pew'
                modeller.addSolvent(forcefield,model=model_water, padding=water_padding_distance * unit.nanometers, positiveIon=water_positive_ion, negativeIon=water_negative_ion, ionicStrength=water_ionicstrength * unit.molar)
            else:
                modeller.addSolvent(forcefield,model=model_water, padding=water_padding_distance * unit.nanometers, positiveIon=water_positive_ion, negativeIon=water_negative_ion, ionicStrength=water_ionicstrength * unit.molar)
        print(f"Protein with buffer solvent prepared")
        
    elif Water_Box == "Absolute":
        if model_water == 'charmm' or model_water == 'explicit' or model_water == 'tip3pfb':
            modeller.addSolvent(forcefield, boxSize=Vec3(water_box_x, water_box_y, water_box_z) * unit.nanometers, positiveIon=water_positive_ion, negativeIon=water_negative_ion, ionicStrength=water_ionicstrength * unit.molar)
        elif model_water == 'implicit' or model_water == 'charmm_tip4pew':
            protein_pdb.addSolvent(boxSize=Vec3(water_box_x, water_box_y, water_box_z) * unit.nanometers, positiveIon=water_positive_ion, negativeIon=water_negative_ion, ionicStrength=water_ionicstrength * unit.molar)
        else:
            if model_water == 'tip4pfb':
                model_water = 'tip4pew'
                modeller.addSolvent(forcefield, model=model_water, boxSize=Vec3(water_box_x, water_box_y, water_box_z) * unit.nanometers, positiveIon=water_positive_ion, negativeIon=water_negative_ion, ionicStrength=water_ionicstrength * unit.molar)
            else:
                modeller.addSolvent(forcefield, model=model_water, boxSize=Vec3(water_box_x, water_box_y, water_box_z) * unit.nanometers, positiveIon=water_positive_ion, negativeIon=water_negative_ion, ionicStrength=water_ionicstrength * unit.molar)
        print(f"Protein with absolute solvent prepared")
    
if add_membrane == True:
    if model_water == 'tip4pew' or model_water == 'tip5p':
        with open(f'pre_converted_{protein}', 'w') as outfile:
            PDBFile.writeFile(modeller.topology, modeller.positions, outfile)
        modeller.convertWater(model_water)
        with open(f'converted_{protein}', 'w') as outfile:
            PDBFile.writeFile(modeller.topology, modeller.positions, outfile)

topology = modeller.topology

positions = modeller.positions

        

# Prepare the Simulation

print('Building system...')
system = forcefield.createSystem(topology, nonbondedMethod=nonbondedMethod, nonbondedCutoff=nonbondedCutoff,
    constraints=constraints, rigidWater=rigidWater, ewaldErrorTolerance=ewaldErrorTolerance, hydrogenMass=hydrogenMass)
system.addForce(MonteCarloBarostat(pressure, temperature, barostatInterval))
integrator = LangevinMiddleIntegrator(temperature, friction, dt)
integrator.setConstraintTolerance(constraintTolerance)
simulation = app.Simulation(topology, system, integrator, platform, platformProperties)
simulation.context.setPositions(positions)

# Minimize and Equilibrate

print('Performing energy minimization...')
simulation.minimizeEnergy()
print('Equilibrating...')
simulation.context.setVelocitiesToTemperature(temperature)
simulation.step(equilibrationSteps)

# Simulate

print('Simulating...')
simulation.reporters.append(PDBReporter(f'output_{protein}', 10000))
simulation.reporters.append(dcdReporter)
simulation.reporters.append(dataReporter)
simulation.reporters.append(checkpointReporter)
simulation.reporters.append(checkpointReporter2)
simulation.reporters.append(checkpointReporter3)
simulation.reporters.append(StateDataReporter(sys.stdout, 1000, step=True, potentialEnergy=True, temperature=True))
simulation.currentStep = 0
simulation.step(steps)