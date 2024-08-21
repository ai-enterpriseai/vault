import pkg_resources
import re

# Load the requirements.txt file from the uploaded file path
file_path = 'requirements.txt'
with open(file_path, 'r') as f:
    requirements = f.read().splitlines()

# Create a list to store the output with versions
output_with_versions = []

# Regular expression to cleanly extract package names (ignores any specifiers)
package_pattern = re.compile(r"^[a-zA-Z0-9_\-]+")

# Iterate through each requirement
for requirement in requirements:
    # Match the package name using regex
    match = package_pattern.match(requirement)
    
    if match:
        req_name = match.group(0)
        # Get the current installed version
        try:
            version = pkg_resources.get_distribution(req_name).version
            output_with_versions.append(f"{req_name}=={version}")
        except pkg_resources.DistributionNotFound:
            output_with_versions.append(f"{req_name}==Not Installed")

# Display the formatted output
formatted_output = "\n".join(output_with_versions)
print(formatted_output)
