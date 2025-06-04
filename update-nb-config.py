#!/usr/bin/env python3
"""
Script to update notebook configuration for EC2 deployment with minikube
"""
import json
import os
import re

def update_notebook_config(notebook_path, host="192.168.49.2", port=30321, model_name="meta-llama/Llama-3.2-3B-Instruct"):
    """Update the HOST, PORT, and MODEL configuration in a Jupyter notebook"""
    
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    modified = False
    
    # Look for cells with HOST, PORT, and MODEL configuration
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            if isinstance(source, list):
                source = ''.join(source)
            
            original_source = source
            
            # Update HOST configuration
            if 'HOST =' in source:
                source = re.sub(
                    r'HOST = ["\'].*?["\'].*',
                    f'HOST = "{host}"  # minikube IP for Llama Stack',
                    source
                )
            
            # Update PORT configuration (handle both PORT and LOCAL_PORT)
            if 'PORT =' in source and 'LOCAL_PORT' not in source and 'CLOUD_PORT' not in source:
                source = re.sub(
                    r'PORT = \d+.*',
                    f'PORT = {port}       # NodePort for Llama Stack in minikube',
                    source
                )
            
            # Update LOCAL_PORT if present
            if 'LOCAL_PORT =' in source:
                source = re.sub(
                    r'LOCAL_PORT = \d+.*',
                    f'LOCAL_PORT = {port}        # NodePort for Llama Stack in minikube',
                    source
                )
            
            # Update CLOUD_PORT if present (keep same as LOCAL_PORT for consistency)
            if 'CLOUD_PORT =' in source:
                source = re.sub(
                    r'CLOUD_PORT = \d+.*',
                    f'CLOUD_PORT = {port}        # NodePort for Llama Stack in minikube',
                    source
                )
            
            # Update MODEL_NAME configuration
            if 'MODEL_NAME=' in source or 'MODEL_NAME =' in source:
                source = re.sub(
                    r"MODEL_NAME\s*=\s*['\"].*?['\"]",
                    f"MODEL_NAME='{model_name}'",
                    source
                )
            
            # Update MODEL_ID configuration (used in some notebooks)
            if 'MODEL_ID =' in source:
                source = re.sub(
                    r'MODEL_ID = ["\'].*?["\"]',
                    f'MODEL_ID = "{model_name}"',
                    source
                )
            
            # Update base_url in LlamaStackClient calls
            if 'LlamaStackClient(base_url=' in source:
                source = re.sub(
                    r'LlamaStackClient\(base_url=["\']http://.*?["\']',
                    f'LlamaStackClient(base_url="http://{host}:{port}"',
                    source
                )
            
            # Update client initialization with f-string base_url
            if 'base_url=f\'http://{HOST}:{PORT}\'' in source or 'base_url=f"http://{HOST}:{PORT}"' in source:
                # This pattern should work with our updated HOST and PORT variables
                pass  # No change needed, the f-string will use our updated variables
            
            if source != original_source:
                cell['source'] = source.split('\n')
                modified = True
    
    if modified:
        # Write back the notebook
        with open(notebook_path, 'w') as f:
            json.dump(notebook, f, indent=2)
        print(f"Updated configuration in {notebook_path}")
    else:
        print(f"No updates needed for {notebook_path}")

if __name__ == "__main__":
    # Directories containing notebooks
    notebook_dirs = ["docs/zero_to_hero_guide", "docs/notebooks"]
    
    for notebook_dir in notebook_dirs:
        if os.path.exists(notebook_dir):
            print(f"\nProcessing directory: {notebook_dir}")
            for filename in os.listdir(notebook_dir):
                if filename.endswith('.ipynb'):
                    notebook_path = os.path.join(notebook_dir, filename)
                    try:
                        update_notebook_config(notebook_path)
                    except Exception as e:
                        print(f"Error updating {notebook_path}: {e}")
        else:
            print(f"Directory {notebook_dir} not found. Run this script from the llama-stack root directory.") 