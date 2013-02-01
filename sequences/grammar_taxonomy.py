import networkx as nx
#import matplotlib.pyplot as plt
import re
from collections import defaultdict

OTHER_OPTION = '[other]'


def drawTaxonomyGraph(taxonomy):

    G=nx.DiGraph()
    for child in taxonomy:
        for parent in taxonomy[child]:
            G.add_edge(parent, child, {'weight': 1})
    graphviz_pos = nx.graphviz_layout(G, prog="dot")
    nx.draw_graphviz(G, with_labels=False, node_size=10, font_size = 7, edge_color='g')
    nx.draw_networkx_labels(G, pos = graphviz_pos, font_size = 7)
    plt.savefig("taxonomy.png")


def get_nodes(grammar, variable, parent_node = None):

    if parent_node is None:
        parent_node = variable

    variable_regex = r'\$(\w+)(\[([\w \/]+?)\])?'

    for value in grammar[variable]:
        # OTHER_OPTION is handled by replacing it with #other_[variable_name], e.g. #other_type_of_animal. This is also done in the data sequences.
        if value == OTHER_OPTION:
            value = '#other_' + variable
        if '$' + variable in parent_node:
            value = parent_node.replace('$' + variable, value)
        child_node = re.sub(variable_regex, lambda match: ('' if value == match.group(0) else '$') + match.group(1), value)
        yield (child_node, parent_node)

        for match in re.findall(variable_regex, value):
                for node in get_nodes(grammar, match[0], child_node):
                    yield node


def merge_grammars(grammar1, grammar2):
    grammar = defaultdict(list)
    for key in grammar1:
        grammar[key] += grammar1[key]
    for key in grammar2:
        grammar[key] += grammar2[key]
    return dict(grammar)

def get_taxonomy():

    # one to one copy of grammar.php
    grammar = {
        'utterance': ['Yes.', 'Yes, $reason_to_say_yes.', 'No.', 'No, $reason_to_say_no.', '$greet[Greet/thank/excuse]', '$assertion[State a fact]', '$question[Ask a question]'],

        'assertion': ['That\'s good.', 'I\'m not sure.', 'I don\'t understand.'],
        'question': ['What do you mean?'],
        'greet': ['Hello.', 'Goodbye.', 'Thank you.', 'I am sorry.'],

        'reason_to_say_yes': ['that\'s possible', 'that is okay', OTHER_OPTION],
        'reason_to_say_no': ['that\'s not possible', 'that is not okay', OTHER_OPTION],

        'type_of_animal': ['cat', 'dog', 'goldfish', 'hamster', 'parrot', OTHER_OPTION],
        'sum_of_money': ['5', '10', '15', '20', OTHER_OPTION],
        'pet_property': ['big', 'small', 'friendly', 'alert', 'cheap in maintenance', 'faithful',
                                'talkative', 'pettable', 'a good breed', OTHER_OPTION],
    }

    customer_grammar = {
        'assertion': ['That is too expensive.'],
        'reason_to_say_yes': ['I need to know more'],
        'reason_to_say_no': ['I know enough'],
        'question': ['What pets do you sell?', 'Can you tell me if a $type_of_animal is $pet_property?', 'Do you sell $type_of_animal?', 'How much does a $type_of_animal cost?', 'What can you tell me about $type_of_animal?', 'I would like to buy a $type_of_animal.', 'Which pet is $pet_property?', 'Give me the $type_of_animal, please.'],
    }

    shopkeep_grammar = {
        'assertion': ['We sell $type_of_animal.', 'We don\'t have $type_of_animal in stock.', 'A $type_of_animal costs $sum_of_money euro.', 'A $type_of_animal is a pet that is $pet_property.'],
        'question': ['How may I help you?', 'Would you like to know more?'],
        'greet': ['Welcome.', 'At your service.'],
    }

    # start building the taxonomy
    taxonomy = {#(0, 'utterance'): ['utterance'],
                #(1, 'utterance'): ['utterance'],
                #(0, 'action'): ['action'],
                #(1, 'action'): ['action'],
                #(-1, 'action'): ['action'],
                (0, 'pay_action'): [(0, 'action')],
                (1, 'give_action'): [(1, 'action')],
                (-1, 'leave_action'): [(0, 'action')],
                (-1, 'enter_action'): [(0, 'action')]}

    # mix in customer grammar
    prefix = 0
    for child, parent in get_nodes(merge_grammars(grammar, customer_grammar), 'utterance'):
        if (prefix, child) in taxonomy:
            taxonomy[(prefix, child)] += [(prefix, parent)]
        else:
            taxonomy[(prefix, child)] = [(prefix, parent)]

    # mix in shopkeep grammar
    prefix = 1
    for child, parent in get_nodes(merge_grammars(grammar, shopkeep_grammar), 'utterance'):
        if (prefix, child) in taxonomy:
            taxonomy[(prefix, child)] += [(prefix, parent)]
        else:
            taxonomy[(prefix, child)] = [(prefix, parent)]

    return taxonomy

if __name__ == "__main__":
    drawTaxonomyGraph(get_taxonomy())
