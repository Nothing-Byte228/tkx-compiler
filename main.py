import argparse
import os
import sys
from core.builders.compiler_builder import CompilerBuilder
from core.config import Config, ProjectTemplate
from core.logger import configure_logging
from core.packager import AppPackager
from cli.enhanced_cli import CLIOutput


def main():
    """Main entry point for tkx-compiler CLI."""
    # Configure CLI argument parser
    cli_parser = argparse.ArgumentParser(
        description="tkx-compiler: Build zero-dependency Python GUI apps from XML markup."
    )
    
    # Subcommands
    subparsers = cli_parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command (default)
    build_parser = subparsers.add_parser("build", help="Build a project")
    build_parser.add_argument(
        "project_path", 
        help="Path to the directory containing your main.xml file"
    )
    build_parser.add_argument(
        "-o", "--output", 
        default="program.py", 
        help="Name of the compiled output Python file (default: program.py)"
    )
    build_parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Show detailed logs during recursive dependency extraction"
    )
    build_parser.add_argument(
        "-c", "--config", 
        help="Path to configuration file"
    )
    build_parser.add_argument(
        "--no-color", 
        action="store_true", 
        help="Disable colored output"
    )
    build_parser.add_argument(
        "--no-progress", 
        action="store_true", 
        help="Disable progress bars"
    )
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument(
        "project_path",
        help="Path where to create the new project"
    )
    init_parser.add_argument(
        "-n", "--name",
        default="tkx_project",
        help="Project name (default: tkx_project)"
    )
    init_parser.add_argument(
        "-t", "--template",
        choices=["basic", "advanced"],
        default="basic",
        help="Project template (default: basic)"
    )
    
    # Package command
    package_parser = subparsers.add_parser("package", help="Package application to executable")
    package_parser.add_argument(
        "project_path",
        help="Path to project directory"
    )
    package_parser.add_argument(
        "-s", "--script",
        help="Path to Python script to package (default: dist/program.py)"
    )
    package_parser.add_argument(
        "-o", "--output",
        default="app",
        help="Output executable name (default: app)"
    )
    package_parser.add_argument(
        "--icon",
        help="Path to icon file (.ico)"
    )
    package_parser.add_argument(
        "--windowed",
        action="store_true",
        help="Create windowed executable (no console)"
    )
    package_parser.add_argument(
        "--no-onefile",
        action="store_true",
        help="Create directory instead of single file"
    )
    
    # Parse arguments
    args = cli_parser.parse_args()
    
    # Handle backward compatibility - if no subcommand, treat as build
    if args.command is None:
        # Re-parse with build subcommand for backward compatibility
        build_args = ["build"] + sys.argv[1:]
        args = cli_parser.parse_args(build_args)
    
    if args.command == "build":
        # Load configuration
        config = Config(args.config) if args.config else Config()
        
        # Override config with CLI arguments
        if args.output != "program.py":
            config.set("output_file", args.output)
        if args.verbose:
            config.set("verbose", True)
        
        # Configure logging
        log_level = "DEBUG" if config.get("verbose", False) else config.get("log_level", "INFO")
        configure_logging(log_level)
        
        # Initialize enhanced CLI output
        cli_output = CLIOutput(
            use_colors=not args.no_color,
            use_progress=not args.no_progress
        )
        
        cli_output.print_header("TKX-COMPILER BUILD")
        cli_output.print_info(f"Project: {args.project_path}")
        cli_output.print_info(f"Output: {config.get('output_file', 'program.py')}")
        cli_output.print_info(f"Verbose: {config.get('verbose', False)}")
        print()
        
        # Create and execute compiler builder
        builder = CompilerBuilder(
            project_path=args.project_path,
            output_file=config.get("output_file", "program.py"),
            verbose=config.get("verbose", False)
        )
        
        result = builder.build()
        
        if result is None:
            cli_output.print_error("Build failed")
            exit(1)
        else:
            cli_output.print_success(f"Build completed successfully: {result}")
    
    elif args.command == "init":
        try:
            if args.template == "basic":
                ProjectTemplate.create_basic_template(args.project_path, args.name)
            else:
                ProjectTemplate.create_advanced_template(args.project_path, args.name)
            print(f"Project initialized successfully at: {args.project_path}")
        except Exception as e:
            print(f"Error initializing project: {e}")
            exit(1)
    
    elif args.command == "package":
        # Initialize enhanced CLI output
        cli_output = CLIOutput(use_colors=True, use_progress=True)
        
        cli_output.print_header("TKX-COMPILER PACKAGE")
        
        # Determine script path
        script_path = args.script or os.path.join(args.project_path, "dist", "program.py")
        
        if not os.path.exists(script_path):
            cli_output.print_error(f"Script not found: {script_path}")
            exit(1)
        
        cli_output.print_info(f"Script: {script_path}")
        cli_output.print_info(f"Output: {args.output}")
        cli_output.print_info(f"Windowed: {args.windowed}")
        cli_output.print_info(f"One-file: {not args.no_onefile}")
        print()
        
        # Create packager
        packager = AppPackager(args.project_path)
        
        # Package application
        exe_path = packager.package_to_exe(
            script_path=script_path,
            output_name=args.output,
            icon_path=args.icon,
            one_file=not args.no_onefile,
            windowed=args.windowed
        )
        
        if exe_path:
            cli_output.print_success(f"Executable created: {exe_path}")
        else:
            cli_output.print_error("Packaging failed")
            exit(1)


if __name__ == "__main__":
    main()
