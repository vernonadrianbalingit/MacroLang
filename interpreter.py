import sys
import os
import re

# Constants for calorie calculations, these are standard everywherew
PROTEIN_CALORIES_PER_GRAM = 4
CARBS_CALORIES_PER_GRAM = 4
FATS_CALORIES_PER_GRAM = 9

# Activity level multipliers for BMR
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,  # lazy
    'moderate': 1.55,  # 3 to 5 days of exercise
    'active': 1.725,   # athelete bro, 5-7 days a week 
}


#there are our goals 
OBJECTIVE_ADJUSTMENTS = {
    'maintain': 1.0,   # No adjustment
    'cut': 0.8,        # 20% deficit
    'bulk': 1.15,      # 15% surplus
}

# Default macro ratios taken from healtline and some werew   guessed 
DEFAULT_MACRO_RATIOS = {
    'maintain': {'protein': 0.3, 'carbs': 0.4, 'fats': 0.3},
    'cut': {'protein': 0.4, 'carbs': 0.4, 'fats': 0.2},
    'bulk': {'protein': 0.4, 'carbs': 0.5, 'fats': 0.2},
}

class MacroLangParser:
    def __init__(self):
        #Initialize the parser.
        self.variables = {}
        self.foods = []
        self.goal = None
        self.operations = []
    
    def parse(self, file_path):
       
        print(f"Parsing file: {file_path}")
        with open(file_path, 'r') as file:
            line_number = 0
            current_statement = None
            current_statement_type = None
            
            for line in file:
                line_number += 1
                line = line.strip()
                
                # we will use this to skip empty lines and comments
                if not line or line.startswith('//'):
                    continue
                
                print(f"Line {line_number}: {line}")
                
                # new stamt
                if line.endswith(':'):
                    # will look at the previous statemnet
                    if current_statement:
                        self.process_statement(current_statement_type, current_statement)
                    
                    # create new statement 
                    current_statement = {}
                    if line.startswith('food'):
                        current_statement_type = 'food'
                        current_statement['name'] = line[5:-1].strip()
                    elif line.startswith('goal'):
                        current_statement_type = 'goal'
                    else:
                        print(f"  Warning: Unknown statement type at line {line_number}")
                        current_statement = None
                        current_statement_type = None
                
                # Calculate statmt
                elif line.startswith('calculate'):
                    parts = line[10:].split('=', 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        value_str = parts[1].strip()
                        
                        # arithmetics
                        if '+' in value_str or '-' in value_str or '*' in value_str or '/' in value_str:
                            try:
                                # change variable with vars
                                expression = value_str
                                for var_name, var_value in self.variables.items():
                                    expression = expression.replace(var_name, str(var_value))
                                
                                # dividison
                                if '/' in expression:
                                    expression = expression.replace('/', '//')
                                
                                # evaluate the epxr
                                result = eval(expression)
                                self.variables[name] = int(result)
                                self.operations.append({
                                    'type': 'calculate',
                                    'name': name,
                                    'expression': value_str,
                                    'result': int(result)
                                })
                                print(f"  Calculated: {name} = {value_str} = {int(result)}")
                            except Exception as e:
                                print(f"  Error evaluating expression: {e}")
                                self.variables[name] = 0
                        else:
                            # simple ssesmet
                            try:
                                value = int(value_str)
                                self.variables[name] = value
                                self.operations.append({
                                    'type': 'calculate',
                                    'name': name,
                                    'value': value
                                })
                                print(f"  Assigned: {name} = {value}")
                            except ValueError:
                                # var reference 
                                if value_str in self.variables:
                                    self.variables[name] = self.variables[value_str]
                                    self.operations.append({
                                        'type': 'calculate',
                                        'name': name,
                                        'value': self.variables[value_str]
                                    })
                                    print(f"  Assigned: {name} = {value_str} = {self.variables[name]}")
                                else:
                                    print(f"  Warning: Undefined variable '{value_str}' at line {line_number}")
                                    self.variables[name] = 0
                
                # properites of each statement 
                elif current_statement is not None:
                    # Food
                    if current_statement_type == 'food':
                        if line.startswith('protein'):
                            current_statement['protein'] = self.process_value(line[8:].strip())
                        elif line.startswith('carbs'):
                            current_statement['carbs'] = self.process_value(line[6:].strip())
                        elif line.startswith('fats'):
                            current_statement['fats'] = self.process_value(line[5:].strip())
                    
                    # Goal
                    elif current_statement_type == 'goal':
                        if line.startswith('height'):
                            current_statement['height'] = self.process_value(line[7:].strip())
                        elif line.startswith('weight'):
                            current_statement['weight'] = self.process_value(line[7:].strip())
                        elif line.startswith('activity'):
                            current_statement['activity'] = line[9:].strip()
                        elif line.startswith('objective'):
                            current_statement['objective'] = line[10:].strip()
            
            # Process stmt
            if current_statement:
                self.process_statement(current_statement_type, current_statement)
        
        return {
            'variables': self.variables,
            'foods': self.foods,
            'goal': self.goal,
            'operations': self.operations
        }
    
    def process_statement(self, stmt_type, stmt):
        #complete statment handlng 
        if stmt_type == 'food':
            # Ensure all macros have values
            if 'protein' not in stmt:
                stmt['protein'] = 0
            if 'carbs' not in stmt:
                stmt['carbs'] = 0
            if 'fats' not in stmt:
                stmt['fats'] = 0
            
            # list for foods 
            self.foods.append(stmt)
            print(f"  Added food: {stmt['name']} with protein={stmt['protein']}, carbs={stmt['carbs']}, fats={stmt['fats']}")
        
        elif stmt_type == 'goal':
            # save the goal 
            self.goal = stmt
            print(f"  Set goal: height={stmt.get('height', 0)}, weight={stmt.get('weight', 0)}, activity={stmt.get('activity', 'moderate')}, objective={stmt.get('objective', 'maintain')}")
    
    def process_value(self, value_str):
        # string to get an int
        try:
            # hard trying to go to an int
            return int(value_str)
        except ValueError:
            # could be referencing a var 
            if value_str in self.variables:
                return self.variables[value_str]
            else:
                print(f"  Warning: Undefined variable '{value_str}'. Using 0.")
                return 0

class MacroLangInterpreter:
    #interpreter
    
    def __init__(self):
        #activate interpreter
        self.variables = {}
    
    def interpret(self, file_path):
        #get the interpreter form the file 
        # Parse the file
        parser = MacroLangParser()
        parsed_data = parser.parse(file_path)
        
        # get data from parsed result
        self.variables = parsed_data['variables']
        foods = parsed_data['foods']
        goal = parsed_data['goal']
        operations = parsed_data['operations']
        
        # Calculate   macros from foods
        total_protein = sum(food['protein'] for food in foods)
        total_carbs = sum(food['carbs'] for food in foods)
        total_fats = sum(food['fats'] for food in foods)
        
        # get total calories
        total_calories = (
            total_protein * PROTEIN_CALORIES_PER_GRAM +
            total_carbs * CARBS_CALORIES_PER_GRAM +
            total_fats * FATS_CALORIES_PER_GRAM
        )
        
        # save totals in variables in arr
        self.variables['total_protein'] = total_protein
        self.variables['total_carbs'] = total_carbs
        self.variables['total_fats'] = total_fats
        self.variables['total_calories'] = total_calories
        
        # report generatiuon
        report = {
            'total_macros': {
                'protein': total_protein,
                'carbs': total_carbs,
                'fats': total_fats,
                'calories': total_calories
            },
            'foods': foods,
            'operations': operations
        }
        
        # if there is a goal we can reccommond 
        if goal:
            recommendations = self.generate_recommendations(goal)
            report['recommendations'] = recommendations
            
            # we can compare
            report['comparison'] = self.generate_comparison(
                total_calories, total_protein, total_carbs, total_fats,
                recommendations['calories'], recommendations['protein'],
                recommendations['carbs'], recommendations['fats']
            )
        
        return report
    
    def generate_recommendations(self, goal):
        """Generate nutritional recommendations based on goals."""
        # Calculate BMR assuming age 21, male, handsome filipino 
        height = goal.get('height', 0)
        weight = goal.get('weight', 0)
        bmr = (10 * weight) + (6.25 * height) - (5 * 30) + 5
        
        # change activity level
        activity = goal.get('activity', 'moderate')
        maintenance_calories = bmr * ACTIVITY_MULTIPLIERS[activity]
        
        # account for the objective
        objective = goal.get('objective', 'maintain')
        recommended_calories = maintenance_calories * OBJECTIVE_ADJUSTMENTS[objective]
        
        # calc reccomneded macros
        ratios = DEFAULT_MACRO_RATIOS[objective]
        protein_calories = recommended_calories * ratios['protein']
        carbs_calories = recommended_calories * ratios['carbs']
        fats_calories = recommended_calories * ratios['fats']
        
        protein_grams = int(protein_calories / PROTEIN_CALORIES_PER_GRAM)
        carbs_grams = int(carbs_calories / CARBS_CALORIES_PER_GRAM)
        fats_grams = int(fats_calories / FATS_CALORIES_PER_GRAM)
        
        # Store recommendation
        self.variables['recommended_calories'] = int(recommended_calories)
        self.variables['recommended_protein'] = protein_grams
        self.variables['recommended_carbs'] = carbs_grams
        self.variables['recommended_fats'] = fats_grams
        
        return {
            'bmr': int(bmr),
            'maintenance': int(maintenance_calories),
            'calories': int(recommended_calories),
            'protein': protein_grams,
            'carbs': carbs_grams,
            'fats': fats_grams
        }
    
    def generate_comparison(self, actual_cals, actual_protein, actual_carbs, actual_fats,
                            rec_cals, rec_protein, rec_carbs, rec_fats):
        """Generate comparison report between actual intake and recommendations."""
        # get percentages
        cal_percent = (actual_cals / rec_cals) * 100 if rec_cals > 0 else 0
        protein_percent = (actual_protein / rec_protein) * 100 if rec_protein > 0 else 0
        carbs_percent = (actual_carbs / rec_carbs) * 100 if rec_carbs > 0 else 0
        fats_percent = (actual_fats / rec_fats) * 100 if rec_fats > 0 else 0
        
        # get it in the right format to display it good 
        cal_diff = f"{cal_percent:.1f}%"
        protein_diff = f"{protein_percent:.1f}%"
        carbs_diff = f"{carbs_percent:.1f}%"
        fats_diff = f"{fats_percent:.1f}%"
        
        # give advice
        cal_advice = "on target" if 95 <= cal_percent <= 105 else "too low" if cal_percent < 95 else "too high"
        protein_advice = "on target" if 95 <= protein_percent <= 105 else "too low" if protein_percent < 95 else "too high"
        carbs_advice = "on target" if 95 <= carbs_percent <= 105 else "too low" if carbs_percent < 95 else "too high"
        fats_advice = "on target" if 95 <= fats_percent <= 105 else "too low" if fats_percent < 95 else "too high"
        
        return {
            'calories': (cal_diff, cal_advice, cal_percent),
            'protein': (protein_diff, protein_advice, protein_percent),
            'carbs': (carbs_diff, carbs_advice, carbs_percent),
            'fats': (fats_diff, fats_advice, fats_percent)
        }
    
    def protein_fizzbuzz_full(self, protein_amount):
        #Fizz Buzz but with PROTEIN and SHAKE, will use the protein intake
        result = []
        
        for i in range(1, protein_amount + 1):
            if i % 3 == 0 and i % 5 == 0:
                result.append("PROTEINSHAKE")
            elif i % 3 == 0:
                result.append("PROTEIN")
            elif i % 5 == 0:
                result.append("SHAKE")
            else:
                result.append(str(i))
        
        return result

def generate_visual_bar(percentage, width=50):
    #Visuals of comparisons 
    filled_width = int((percentage / 100) * width)
    if filled_width > width:
        filled_width = width
    
    bar = '█' * filled_width + '░' * (width - filled_width)
    return f"[{bar}] {percentage:.1f}%"

def display_report(report):
    # make a report 
    print("\n===== MacroLang Report =====\n")
    
    # Display arithmetic operations
    calc_operations = [op for op in report.get('operations', []) if op.get('type') == 'calculate' and 'expression' in op]
    if calc_operations:
        print("Arithmetic Operations:")
        for op in calc_operations:
            print(f"  {op['name']} = {op['expression']} = {op['result']}")
        print()
    
    # Display total macros
    print("Total Macros:")
    print(f"  Protein: {report['total_macros']['protein']}g")
    print(f"  Carbs: {report['total_macros']['carbs']}g")
    print(f"  Fats: {report['total_macros']['fats']}g")
    print(f"  Calories: {report['total_macros']['calories']} kcal")
    
    # Display calculations if theree
    calculations = [op for op in report.get('operations', []) if op.get('type') == 'calculate' and 'value' in op]
    if calculations:
        print("\nCalculations:")
        for calc in calculations:
            print(f"  {calc['name']} = {calc['value']}")
    
    # Display FizzBuzz result for protein
    protein_amount = report['total_macros']['protein']
    interpreter = MacroLangInterpreter()
    
    # Generate complete FizzBuzz sequence
    fizzbuzz_sequence = interpreter.protein_fizzbuzz_full(protein_amount)
    
    print("\nProtein FizzBuzz Sequence:")
    # put it in rows
    row_length = 10
    for i in range(0, len(fizzbuzz_sequence), row_length):
        row = fizzbuzz_sequence[i:i+row_length]
        print("  " + ", ".join(row))
    
    # show reccomndations if present 
    if 'recommendations' in report:
        rec = report['recommendations']
        print("\nRecommended Daily Intake:")
        print(f"  BMR: {rec['bmr']} kcal")
        print(f"  Maintenance: {rec['maintenance']} kcal")
        print(f"  Target Calories: {rec['calories']} kcal")
        print(f"  Protein: {rec['protein']}g")
        print(f"  Carbs: {rec['carbs']}g")
        print(f"  Fats: {rec['fats']}g")
    
    # showw comparison if present
    if 'comparison' in report:
        comp = report['comparison']
        print("\nComparison to Recommendations:")
        
        #cool bar for calories
        cal_percent = comp['calories'][2]
        cal_bar = generate_visual_bar(cal_percent)
        print(f"  Calories: {cal_bar} ({comp['calories'][1]})")
        
        # col bar for protein
        protein_percent = comp['protein'][2]
        protein_bar = generate_visual_bar(protein_percent)
        print(f"  Protein: {protein_bar} ({comp['protein'][1]})")
        
        # cool bar for carbs
        carbs_percent = comp['carbs'][2]
        carbs_bar = generate_visual_bar(carbs_percent)
        print(f"  Carbs: {carbs_bar} ({comp['carbs'][1]})")
        
        # cool bar for fats
        fats_percent = comp['fats'][2]
        fats_bar = generate_visual_bar(fats_percent)
        print(f"  Fats: {fats_bar} ({comp['fats'][1]})")
        
        # Overall report
        all_on_target = all(advice == "on target" for _, advice, _ in comp.values())
        any_too_high = any(advice == "too high" for _, advice, _ in comp.values())
        
        print("\nOverall Assessment:")
        if all_on_target:
            print("  Great job! You're meeting all your macro targets.")
        elif any_too_high:
            print("  Consider adjusting your intake to better match your goals.")
        else:
            print("  You may need to increase some macros to meet your targets.")

def main():
    # run all 
    # Check if file was provided
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <macrolang_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    # Use our own parser and interpreter
    try:
        interpreter = MacroLangInterpreter()
        report = interpreter.interpret(file_path)
        display_report(report)
    except Exception as e:
        print(f"Error interpreting file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()