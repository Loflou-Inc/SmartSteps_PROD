def main():
    """
    Main function.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description="Security audit for Smart Steps AI")
    parser.add_argument("--api-url", type=str, help="URL of the API server", default="http://localhost:8000")
    parser.add_argument("--output-dir", type=str, help="Directory to store results", default="results")
    parser.add_argument("--skip-api", action="store_true", help="Skip API security checks")
    parser.add_argument("--skip-code", action="store_true", help="Skip code scanning")
    parser.add_argument("--skip-dependencies", action="store_true", help="Skip dependency checks")
    parser.add_argument("--skip-data-protection", action="store_true", help="Skip data protection checks")
    parser.add_argument("--skip-input-validation", action="store_true", help="Skip input validation checks")
    args = parser.parse_args()
    
    # Print header
    console.print(Panel.fit("[bold]Smart Steps AI Security Audit[/bold]"))
    console.print(f"API URL: {args.api_url}")
    console.print(f"Output directory: {args.output_dir}")
    console.print("")
    
    # Create results directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize findings
    findings = {}
    
    # Check dependencies
    if not args.skip_dependencies:
        try:
            dependency_findings = check_dependency_vulnerabilities()
            findings["dependencies"] = dependency_findings
        except Exception as e:
            console.print(f"[red]Error checking dependencies: {e}[/red]")
            findings["dependencies"] = []
    
    # Scan code
    if not args.skip_code:
        try:
            code_findings = scan_code_for_vulnerabilities()
            findings["code"] = code_findings
        except Exception as e:
            console.print(f"[red]Error scanning code: {e}[/red]")
            findings["code"] = []
    
    # Check API security
    if not args.skip_api:
        try:
            api_findings = check_api_security(args.api_url)
            findings["api"] = api_findings
        except Exception as e:
            console.print(f"[red]Error checking API security: {e}[/red]")
            findings["api"] = []
    
    # Check data protection
    if not args.skip_data_protection:
        try:
            data_protection_findings = check_data_protection()
            findings["data_protection"] = data_protection_findings
        except Exception as e:
            console.print(f"[red]Error checking data protection: {e}[/red]")
            findings["data_protection"] = []
    
    # Check input validation
    if not args.skip_input_validation:
        try:
            input_validation_findings = check_input_validation()
            findings["input_validation"] = input_validation_findings
        except Exception as e:
            console.print(f"[red]Error checking input validation: {e}[/red]")
            findings["input_validation"] = []
    
    # Generate report
    try:
        report_path = generate_report(findings, args.output_dir)
        console.print(f"[green]Security audit completed. Report saved to: {report_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")

if __name__ == "__main__":
    main()
