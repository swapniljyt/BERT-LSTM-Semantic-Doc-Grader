import re
import warnings
import pandas as pd

def calculate_similarity_scores(evaluator_content, student_content,model):
    model=model
    def create_dictionary(content):
        # Remove numeric indices before "Question" and "Answer" words, preserving the colon
        content_without_indices = re.sub(r'(\b\d+\.\s*Question:)', 'Question:', content)
        content_without_indices = re.sub(r'(\b\d+\.\s*Answer:)', 'Answer:', content_without_indices)

        # Tokenize and print each word with punctuation
        words = re.findall(r'\b\w+\b|[.,;!?:]', content_without_indices)

        sentence = ""
        my_dic = {}
        n = 0

        for word in words:
            if word == "Answer" and words[n + 1] == ":":
                key = sentence.strip()
                sentence = ""
            if word == "Question" and n > 4 and words[n + 1] == ":":
                my_dic[key] = sentence.strip()
                sentence = ""
            sentence += word
            sentence += " "
            n += 1

        # Check for the last question-answer pair
        if sentence.strip() and key:
            my_dic[key] = sentence.strip()

        return my_dic

    eval_dic = create_dictionary(evaluator_content)
    std_dic = create_dictionary(student_content)

    data = {'Evaluator': [], 'Student': [], 'per_mark': [], 'Similarity': []}
    total_entailment = 0
    total_neutral = 0
    total_contradiction = 0

    for fn in eval_dic.keys():
        sentence_1 = eval_dic[fn]
        sentence_2 = std_dic[fn]
        result = check_similarity(sentence_1, sentence_2,model)

        # Extracting percentage value from the tuple
        percentage = float(result[1].strip('%'))

        data['Student'].append(sentence_2)
        data['Evaluator'].append(sentence_1)
        data['per_mark'].append(percentage)
        data['Similarity'].append(result[0])

        # Update total scores based on result type
        if result[0] == 'entailment':
            total_entailment += percentage
        elif result[0] == 'neutral':
            total_neutral += percentage / 3
        elif result[0] == 'contradiction':
            total_contradiction += percentage

    # Calculate average scores
    num_entailment = len([x for x in data['Similarity'] if x == 'entailment'])
    num_neutral = len([x for x in data['Similarity'] if x == 'neutral'])
    num_contradiction = len([x for x in data['Similarity'] if x == 'contradiction'])

    num = (num_entailment + num_neutral + num_contradiction)
    total_contradiction=0
    total_accuracy = (total_contradiction + total_entailment + total_neutral) / num

    # Add total accuracy to DataFrame
    data['Total_Accuracy'] = total_accuracy

    df = pd.DataFrame(data)
    return df