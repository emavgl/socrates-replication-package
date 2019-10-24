# Notes
1. [Source Code](#Source-Code)
2. [Generate AST](#Generate-AST)
3. [AST Visit](#AST-Visit)
4. [Mapping to Z3](#Mapping-to-Z3)

### Source code

The code can be summarized in few main steps:

```py
# Compile, Generate AST
ast_json = asthelper.compile(filename)

# Visit
inspected_function = astvisitor.visitAst(ast_json, function_name)

# Map to Z3
z3_generated_code = mapper.ast_to_z3(inspected_function)

# Write On File
output_file_path = filewriter.write_z3_script(function_name, z3_generated_code)
```

### Generate AST

```
solc --ast-compact-json > eip_ast.json
```

The output is a json of this form:

```
JSON AST (compact format):


======= EIP20.sol =======
{
    ...
}
======= EIP20Interface.sol =======
{
    ...
}
```

To import the file as json, it is needed to the remove all the headers first.
Then, for each file, we have an object like:

```
{
	"absolutePath" : "EIP20.sol",
	"exportedSymbols" : 
	{
		"EIP20" : 
		[
			266
		]
	},
	"id" : 267,
	"nodeType" : "SourceUnit",
	"nodes" : [...]
	"src" : "102:3540:0"
}
```

In nodes we have a list of nodes. Each node represents the information such
as the content of a block, or a statements, or an import and so on.
Each node contains different information. A node can have nested nodes (for example, a node which identifies a contract has a nested list *nodes*).

To identify the nature of the node there is a field that is called: **nodeType**.
We distinguish different node types:

- *PragmaDirective*: identifies the version of solidity
- *ImportDirective*: import of another solidity file
- *ContractDefinition*: containing all the information of a contract definition
- *VariableDeclaration*
- *ExpressionStatement*
- *Block*
  - statement: ExpressionStatement[]
- *FunctionDefinition*
- *ParameterList* 
    - body
      - Block
    - FunctionDefinition
    - name: String
    - parameters: ParameterList
    - returnParameters: ParameterList
    - visibility: String
    - ...
    
The definition of the AST is omitted for brevity and the fields useful
for the visit will be described in the next sections.

### AST Visit

We are looking for all those statements before the last *require* of
the function under test. Of all these statements we are interested in:

- local variables declarations
- accessed state variables
- requires' conditions

**Assumption:** if those statements contain a loop, condition, function call,
assignment, the script cannot proceed and will throw an exception.

To facilitate the visit and the search we implemented the module *asthelper*
which includes two methods *find_node(options)* and *find_all_nodes(options)*. The methods recursively
visit the tree until their find the node or the nodes with the requested fields *options*.

The results of the visit is an object with the fields:

- *formal_parameters*
- *local_variables_ids*
- *state_variables_ids* 
- *requires*
- *local_variables*
- *accessed_state_variables*
- *candidate_for_overflow*

### Mapping to Z3

The objective is to use the information extracted in the previous step to
to create constraints. Those constraints are then used in the Z3's solver.
The solver will find the concrete values for the formal parameters in order
to have an integer overflow at least in one of the candidate local variables.

#### Types

All the types are expressed using integers.
Whenever in the code there is a variable of type `address`, it is converted to
an integer symbolic variables which indicated the index of address inside the
array of all the possible accounts.

String, Bytes are not supported.

#### Z3 Array

A solidity map `es. mapping(address -> uint)` is a data structure in which you can
access using an address as index and the corresponding value is of type *uint*.
Those types are commonly used to express state variables. The script **does not**
support mapping as local variables. The map is converted using a Z3 Array,
an array of infinite length, accessible using a symbolic variables.

A case use is the variable `balances` that is a `mapping(address -> uint256)`.
A new symbolic Array `balances` will be created, and the concrete values
(*current balance for each address*) will be compied in this Array using the Z3's
function *Store*.

Then, the access `balances[msg.sender]` will be converted into `balances[msg_sender]`
where msg_sender is a symbolic variables. Z3 will find the symbolic index *msg_send* (*account*)
such that the accessed (*balance of that user*) respect some requirements.

#### Z3 IntVector

Then, Solidity supports [array](http://solidity.readthedocs.io/en/v0.4.24/types.html#arrays).
A solidity program accesses the element inside the array, or the member `length` which returns
the size of the array.

So, an array it is mapped into two Z3 symbolic variables.
The first, is `IntVector` of fixed size, in which is a set of symbolic
variables which represents the element inside the array. The second is
instead a symbolic variables representing the length of that array.

```
_receivers = IntVector('_receivers', max_array_len)
_receivers_length = Int('_receivers_length')
solver.add(_receivers_length >= 0, _receivers_length < max_array_len)
for x in _receivers: solver.add(x >= -1, x < accounts_len)
```

Using the following constraints we ensure that to all the elements
in the list have a non-negative values.

```
solver.add(_receivers_length == Sum([If(x >= 0, 1, 0) for x in _receivers]))
```

Once declared, you can have access to members using a (**not symbolic**) integer index.
This means that member can be enumerated (for example can be accessed in a for loop).   

You can have constraints on array elements, for examples:

`balances[receivers[0]] > 0`

  
List are supported as **formal parameter**.  
But **not supported** as *state variable*.