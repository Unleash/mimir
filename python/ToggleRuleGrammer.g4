grammar ToggleRuleGrammer;

expr:
	PARAM_VALUE expr				# ParamExpr
	| '(' expr ')'					# ParenExpr
	| atom = STRATEGY				# StratExpr
	| left = expr AND right = expr	# AndExpr
	| left = expr OR left = expr	# OrExpr
	| NOT expr						# NotExpr
	| atom = BOOLEAN				# BoolExpr
	| constraint					# ConstraintExpr;

valued_expression: (numeric | string | context);
context: CONTEXT_VALUE '(' data = string ')';

numeric: (STRING | FLOAT | INT) # NumericExpr;
string: STRING;
props: '{' STRING ':' STRING '}' # PropsExpr;
listy: '[]' | '[' numeric (COMMA numeric)* ']';

constraint:
	left = valued_expression op = NUMERIC_OPERATOR right = valued_expression	# NumericConstraintExpr
	| left = valued_expression op = CONTAINS_OPERATOR right = listy				# ContainsConstraintExpr;

STRATEGY: ('gradualRolloutRandom' | 'gradualRolloutSessionId');

CONTAINS_OPERATOR: ('IN' | 'NOT_IN');
SEMVER_OPERATOR: ('SEMVER_EQ' | 'SEMVER_LT');
NUMERIC_OPERATOR: (
		'NUM_EQ'
		| 'NUM_GTE'
		| 'NUM_LTE'
		| 'NUM_GT'
		| 'NUM_LT'
	);

PARAM_VALUE: 'PARAM_VALUE';
CONTEXT_VALUE: ('contextValue');

NOT: 'NOT';
AND: 'AND';
OR: 'OR';

BOOLEAN: ('true' | 'false');
STRING: '"' (~["\r\n] | '""')* '"';
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]* | '.' [0-9]+;

COMMA: ',';

WS: [ \t]+ -> skip;