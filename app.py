import streamlit as st
from difflib import SequenceMatcher
import re
import hashlib
import ast
import networkx as nx
from networkx.algorithms import isomorphism

# Helper functions for preprocessing and hashing code
def preprocess_code(code):
    code = re.sub(r'//.*|/\*[\s\S]*?\*/|#.*', '', code)  # Remove comments
    code = re.sub(r'".*?"|\'.*?\'', '', code)  # Remove string literals
    code = re.sub(r'\s+', ' ', code).strip()  # Normalize code
    code = code.lower()  # Convert to lowercase
    return code

def generate_code_hash(code):
    cleaned_code = preprocess_code(code)
    return hashlib.md5(cleaned_code.encode()).hexdigest()

def compare_codes_hash_based(original_code, plagiarized_code):
    original_hash = generate_code_hash(original_code)
    plagiarized_hash = generate_code_hash(plagiarized_code)
    if original_hash == plagiarized_hash:
        return "1"
    else:
        return "0"

# Helper functions for AST graph-based comparison
def ast_to_graph(node, graph=None):
    if graph is None:
        graph = nx.DiGraph()
    graph.add_node(id(node), type=type(node).__name__)
    for child in ast.iter_child_nodes(node):
        graph.add_node(id(child), type=type(child).__name__)
        graph.add_edge(id(node), id(child))
        ast_to_graph(child, graph)
    return graph

def code_to_graph(code):
    tree = ast.parse(code)
    return ast_to_graph(tree)

def compare_graphs(graph1, graph2):
    def node_match(node1, node2):
        return node1['type'] == node2['type']
    GM = isomorphism.DiGraphMatcher(graph1, graph2, node_match=node_match)
    return GM.subgraph_is_isomorphic()

def compare_codes_ast_based(original_code, plagiarized_code):
    graph1 = code_to_graph(original_code)
    graph2 = code_to_graph(plagiarized_code)
    is_similar = compare_graphs(graph1, graph2)
    if is_similar:
        return "1"
    else:
        return "0"

# Helper functions for code with variable replacement
def preprocess_code_with_variable_replacement(code):
    code = re.sub(r'//.*|/\*[\s\S]*?\*/|#.*', '', code)  # Remove comments
    code = re.sub(r'".*?"|\'.*?\'', '', code)  # Remove string literals
    tokenized_code = replace_variable_names_and_functions(code)
    tokenized_code = re.sub(r'\s+', ' ', tokenized_code).strip()  # Normalize code
    tokenized_code = tokenized_code.lower()  # Convert to lowercase
    return tokenized_code

def replace_variable_names_and_functions(code):
    variable_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
    reserved_keywords = {'def', 'return', 'for', 'while', 'if', 'else', 'elif', 'in', 'print', 'and', 'or', 'not', 'is', 'None', 'True', 'False', 'break', 'continue'}
    tokens = re.findall(variable_pattern, code)
    variable_map = {}
    placeholder_count = 1
    for token in tokens:
        if token not in reserved_keywords:
            if token not in variable_map:
                variable_map[token] = f'var_{placeholder_count}'
                placeholder_count += 1
    for var, placeholder in variable_map.items():
        code = re.sub(r'\b' + re.escape(var) + r'\b', placeholder, code)
    return code

def generate_code_hash_with_replacement(code):
    cleaned_code = preprocess_code_with_variable_replacement(code)
    return hashlib.md5(cleaned_code.encode()).hexdigest()

def compare_codes_variable_replacement(original_code, plagiarized_code):
    original_hash = generate_code_hash_with_replacement(original_code)
    plagiarized_hash = generate_code_hash_with_replacement(plagiarized_code)
    if original_hash == plagiarized_hash:
        return "1"
    else:
        return "0"

# Function to categorize the comparison
def categorize_code_similarity(original_code, plagiarized_code):
    result = []
    
    result.append(compare_codes_hash_based(original_code, plagiarized_code))
    result.append(compare_codes_ast_based(original_code, plagiarized_code))
    result.append(compare_codes_variable_replacement(original_code, plagiarized_code))
    return result

# Example usage with Python code
original_code = '''
class Solution:
    def maximumProduct(self, nums: List[int]) -> int:
        nums.sort()
        return max(nums[-1]*nums[-2]*nums[-3],nums[0]*nums[1]*nums[-1])
'''

plagiarized_code = '''
class Solution:
    def maxPro(self, arr: List[int]) -> int:
        arr.sort()
        return max(arr[-1]*arr[-2]*arr[-3],arr[0]*arr[1]*arr[-1])

'''

# Print the categorization results
# results = categorize_code_similarity(original_code, plagiarized_code)
# for result in results:
#     print(result)







def similarity_score(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

def test_all(text1, text2):
    check_plagiarism(text1,text2)


def check_plagiarism(code1, code2):
    # Remove comments and whitespace for a more accurate comparison
    code1_clean = "\n".join(line.strip() for line in code1.splitlines() if not line.strip().startswith("#"))
    code2_clean = "\n".join(line.strip() for line in code2.splitlines() if not line.strip().startswith("#"))
    
    similarity = similarity_score(code1_clean, code2_clean)
    percentage = similarity * 100
    
    result = f"Similarity Score: {percentage:.2f}%\n"
    if percentage > 80:
        result += "High similarity detected. This may indicate potential plagiarism."
    elif percentage > 50:
        result += "Moderate similarity detected. Further investigation may be needed."
    else:
        result += "Low similarity detected. Plagiarism is unlikely."
    
    return result

def main():
    st.set_page_config(layout="wide")

    st.title("Plagiarism and Cheating Detector")

    # Create two columns for the input boxes
    col1, col2 = st.columns(2)
    list = ["Hash based", "AST based" , "Variable replaced"]
    # Input box for the first code
    with col1:
        code1 = st.text_area("Enter the first code:", height=300)

    # Input box for the second code
    with col2:
        code2 = st.text_area("Enter the second code:", height=300)

    # Store the codes as comments in variables
    original_code = f"''' {code1}'''"
    plagiarized_code = f"''' {code2}'''"



    













    # Button to trigger plagiarism check
    if st.button("Check for Plagiarism"):
        if code1 and code2:
            result = check_plagiarism(original_code, plagiarized_code)
            st.write(result)
            results = categorize_code_similarity(original_code, plagiarized_code)
            st.subheader("Plagiarism Check Result:")
            i = 0 
            res_final=[]
            for result in results:
                if result == "1":
                    res_final.append("True")
                else:
                    res_final.append("False")

            for result in res_final:
                if result == "True":
                    st.warning(list[i]+ " : " + result , icon="⚠️")
                    i+=1
                else:
                    st.success(list[i]+ " : " + result)
                    i+=1
            
            
        else:
            st.warning("Please enter code in both input boxes.")

if __name__ == "__main__":
    main()