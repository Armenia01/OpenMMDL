import os
import shutil
from typing import List


class FileManager:
    """
    A class for file and directory management operations such as
    creating directories, copying files, and organizing files.
    """

    @staticmethod
    def create_directory_if_not_exists(directory_path):
        """Create a directory if it doesn't exist, or overwrite it if already does.

        Args:
            directory_path (str): Path of the directory that you want to create.

        Returns:
            None
        """
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
        else:
            shutil.rmtree(directory_path)
            os.mkdir(directory_path)

    @staticmethod
    def copy_file(src, dest):
        """Copy a file to the destination path.

        Args:
            src (str): Path of the file that needs to be copied.
            dest (str): Path of destination where the file needs to be copied to.

        Returns:
            None
        """
        if os.path.exists(src):
            shutil.copy(src, dest)

    @staticmethod
    def organize_files(source_files, destination):
        """Organizes the files and moves them from the source to the destination directory.

        Args:
            source_files (List[str]): List of paths of the files that need to be moved.
            destination (str): Path of destination where the files need to be moved to.

        Returns:
            None
        """
        for file in source_files:
            if os.path.exists(file):
                os.rename(file, os.path.join(destination, os.path.basename(file)))


class Cleanup:
    """
    A class for cleaning up simulation files.
    """

    @staticmethod
    def cleanup_files(protein_name):
        """Cleans up the PDB Reporter Output File and MDTraj Files of the performed simulation.

        Args:
            protein_name (str): Name of the protein PDB.

        Returns:
            None
        """
        print("Cleaning Up :)")
        try:
            os.remove(f"output_{protein_name}")
            os.remove(f"centered_old_coordinates.pdb")
            os.remove(f"centered_old_coordinates.dcd")
        except FileNotFoundError:
            print("One or more files not found. Cleanup skipped.")
        print("Cleanup is done.")


class PostMDProcessor:
    """
    A class for organizing and moving files after MD simulation.
    """

    @staticmethod
    def post_md_file_movement(
        protein_name: str,
        prmtop: str = None,
        inpcrd: str = None,
        ligands: List[str] = None,
    ):
        """Organizes and moves the files after the MD simulation to their respective directories.

        Args:
            protein_name (str): Name of the protein PDB.
            prmtop (str, optional): Path to the AMBER topology file.
            inpcrd (str, optional): Path to the AMBER coordinate file.
            ligands (List[str], optional): List of paths to the ligand files.

        Returns:
            None
        """
        # Create necessary directories
        dirs = [
            "Input_Files",
            "MD_Files",
            "MD_Files/Pre_MD",
            "MD_Files/Minimization_Equilibration",
            "MD_Files/MD_Output",
            "MD_Postprocessing",
            "Final_Output",
            "Final_Output/All_Atoms",
            "Final_Output/Prot_Lig",
            "Checkpoints",
        ]

        for directory in dirs:
            FileManager.create_directory_if_not_exists(directory)

        # Move input files
        if ligands:
            FileManager.copy_file(ligands, "Input_Files")
            FileManager.copy_file(ligands, "Final_Output/All_Atoms")
            FileManager.copy_file(ligands, "Final_Output/Prot_Lig")

        FileManager.copy_file(protein_name, "Input_Files")
        if prmtop:
            FileManager.copy_file(prmtop, "Input_Files")
        if inpcrd:
            FileManager.copy_file(inpcrd, "Input_Files")

        # Organize pre-MD files
        source_pre_md_files = [
            "prepared_no_solvent_",
            "solvent_padding_",
            "solvent_absolute_",
            "membrane_",
        ]
        destination_pre_md = "MD_Files/Pre_MD"
        FileManager.organize_files(
            [f"{prefix}{protein_name}" for prefix in source_pre_md_files],
            destination_pre_md,
        )

        # Organize topology files after minimization and equilibration
        source_topology_files = ["Energyminimization_", "Equilibration_"]
        destination_topology = "MD_Files/Minimization_Equilibration"
        FileManager.organize_files(
            [f"{prefix}{protein_name}" for prefix in source_topology_files],
            destination_topology,
        )

        # Organize simulation output files
        FileManager.organize_files(
            [f"output_{protein_name}", "trajectory.dcd"], "MD_Files/MD_Output"
        )

        # Organize MDtraj and MDAnalysis files
        postprocessing_files = [
            "centered_old_coordinates_top.pdb",
            "centered_old_coordinates.dcd",
            "centered_old_coordinates_top.gro",
            "centered_old_coordinates.xtc",
            "centered_traj_unaligned.dcd",
            "centered_traj_unaligned.xtc",
            "prot_lig_traj_unaligned.dcd",
            "prot_lig_traj_unaligned.xtc",
        ]
        FileManager.organize_files(postprocessing_files, "MD_Postprocessing")

        all_atoms_files = [
            "centered_top.pdb",
            "centered_traj.dcd",
            "centered_top.gro",
            "centered_traj.xtc",
        ]
        FileManager.organize_files(all_atoms_files, "Final_Output/All_Atoms")

        prot_lig_files = [
            "prot_lig_top.pdb",
            "prot_lig_traj.dcd",
            "prot_lig_top.gro",
            "prot_lig_traj.xtc",
        ]
        FileManager.organize_files(prot_lig_files, "Final_Output/Prot_Lig")

        # Organize checkpoint files
        checkpoint_files = [
            "checkpoint.chk",
            "10x_checkpoint.chk",
            "100x_checkpoint.chk",
        ]
        FileManager.organize_files(checkpoint_files, "Checkpoints")
