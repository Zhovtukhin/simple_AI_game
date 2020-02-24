import sys  # Для помилок
import noun_phrase_ua  # Для обробки укр. мови

# Визначення масивів для дій (окремо для збільшення та зменьшення)
acts_n = ['з\'їв', 'забрав', 'сховав', 'прибрав', 'заховав']  # дії, що зменьшують к-сть предметів на столі
acts_p = ['поклав', 'доніс', 'приєднав', 'докинув', 'повернув']  # дії, що збільшують кількість предметів на столі
# Визначення масиву з фруктами
fruits = ['яблука', 'груші', 'апельсини', 'мандарини', 'банани']

# Застосування NLP для масивів
nlp = noun_phrase_ua.NLP()
acts_lemmas_n = [i['lemma'] for i in nlp.extract_entities(', '.join(acts_n))['tokens'] if i['lemma'] != ',']
acts_lemmas_p = [i['lemma'] for i in nlp.extract_entities(', '.join(acts_p))['tokens'] if i['lemma'] != ',']
fruits_lemmas = [i['lemma'] for i in nlp.extract_entities(', '.join(fruits))['tokens'] if i['lemma'] != ',']
# Обробка виключень множини та слова "мандарина"
for i in range(len(fruits_lemmas)):
    if fruits_lemmas[i] == 'мандарина':
        fruits_lemmas[i] = 'мандарин'
    if fruits_lemmas[i][-1] == 'и':
        fruits_lemmas[i] = fruits_lemmas[i][:-1]


# Функція, що повертає об'єкта та його кількості
def get_pair(tokens, word, i, shift, group=True, plase=''):
    if len(tokens) > i + shift:
        if (not group) and shift == 2:
            if tokens[i + 1]['word'] in [',', ';', '.']:
                return []
        obj = tokens[i + shift]
        if group:
            if obj['word'] in word['groupWord']:
                if obj['lemma'] in fruits_lemmas:
                    return [obj['lemma'], int(word['lemma'])]
                else:
                    # Якщо не знайдено - повернути ближній іменник біля цифри
                    if obj['pos'] == "NOUN":
                        # Об'єктпозначається нулем у кінці масиву, якщо його неемає у масиві фруктів на початку
                        return [obj['lemma'], int(word['lemma']), 0]
                    # Можливо повернути помилку, коли об'єкту нема в масиві з фруктами
                    # sys.exit("Помилка! Біля числа " + word[
                    #    'lemma'] + ' слово - \'' + obj['word'] +
                    #         '\', що не є фруктом або не внесено у масив можливих фруктів. ' + plase)
        else:
            if obj['lemma'] in fruits_lemmas:
                return [obj['lemma'], int(word['lemma'])]
            else:
                if obj['pos'] == "NOUN":
                    return [obj['lemma'], int(word['lemma']), 0]
                # sys.exit("Помилка! Біля числа " + word[
                #    'lemma'] + ' слово - \'' + obj['word'] +
                #         '\', що не є фруктом або не внесено у масив можливих фруктів. ' + plase)
    else:
        if i > shift - 1:
            if (not group) and shift == 2:
                if tokens[i - 1]['word'] in [',', ';', '.']:
                    return []
            obj = tokens[i - shift]
            if obj['lemma'] in fruits_lemmas:
                return [obj['lemma'], int(word['lemma'])]
            else:
                if obj['pos'] == "NOUN":
                    return [obj['lemma'], int(word['lemma']), 0]
                # sys.exit("Помилка! Біля числа " + word[
                #    'lemma'] + ' слово - \'' + obj['word'] +
                #         '\', що не є фруктом або не внесено у масив можливих фруктів. ' + plase)
    sys.exit("Помилка! Біля числа " + word[
        'lemma'] + ' немає об\'єкта. ' + plase)


if __name__ == '__main__':
    # Отримання предметів зі столу
    table = input('Введіть предмети на столі\n')
    table_dict = nlp.extract_entities(table)
    # Пошук чисел
    num = [i for i, word in enumerate(table_dict['tokens']) if word['pos'] == 'NUM']

    # Масив для зберігання позиції, кількості та назви об'єктів
    table_pairs = []
    for i in num:
        word = table_dict['tokens'][i]
        # Якщо задано словом - помилка
        try:
            int(word['lemma'])
        except:
            sys.exit("Помилка! Число: " + word['lemma'] + ' повинно бути написане цифрами. У першому реченні.')

        # Пошук пар об'єкт - число для різних варіантів
        if word['groupLength'] == 2:  # NLP визначило пару для числа
            pair = get_pair(table_dict['tokens'], word, i, 1, plase='У першому реченні')
        elif word['groupLength'] == 3:  # NLP визначило трійку для числа
            pair = get_pair(table_dict['tokens'], word, i, 2, plase='У першому реченні')
        else:
            pair = get_pair(table_dict['tokens'], word, i, 1, False, plase='У першому реченні')
            if not pair:
                pair = get_pair(table_dict['tokens'], word, i, 2, False, plase='У першому реченні')
        if pair:
            if (pair[0] in [p[1] for p in table_pairs]):
                # Помилка, коли лише число
                sys.exit("Помилка! Біля числа " + word['lemma'] + ' немає об\'єкта. У першому реченні')
            table_pairs.append([i] + pair)
    # Оборбка виключень
    for i in range(len(table_pairs)):
        if table_pairs[i][1] == 'мандарина':
            table_pairs[i][1] = 'мандарин'
        if table_pairs[i][-1] == 'и':
            table_pairs[i] = table_pairs[i][:-1]
        if len(table_pairs[i]) == 4 and table_pairs[i][1] == 'мандарин':
            table_pairs[i] = table_pairs[i][:3]
    # print(table_pairs)

    # Отриамння дій, що виконав хлопчик
    act = input('Введіть дії хлопчика\n')
    act_dict = nlp.extract_entities(act)
    neg_acts = [i for i, word in enumerate(act_dict['tokens']) if word['lemma'] in acts_lemmas_n]
    pos_acts = [i for i, word in enumerate(act_dict['tokens']) if word['lemma'] in acts_lemmas_p]
    # Пошук чисел
    num = [i for i, word in enumerate(act_dict['tokens']) if word['pos'] == 'NUM']

    # Масив для збурігання позицій, об'єктів та к-сть на яку він змінився
    act_pairs = []
    for i in num:
        word = act_dict['tokens'][i]
        # Якщо число - слово, то помилка
        try:
            int(word['lemma'])
        except:
            sys.exit("Помилка! Число: " + word['lemma'] + ' повинно бути написане цифрами. У другому реченні.')

        # Пошук пар об'єкт - число
        if word['groupLength'] == 2:
            pair = get_pair(act_dict['tokens'], word, i, 1, plase='У другому реченні')
        elif word['groupLength'] == 3:
            pair = get_pair(act_dict['tokens'], word, i, 2, plase='У другому реченні')
        else:
            pair = get_pair(act_dict['tokens'], word, i, 1, False, plase='У другому реченні')
            if pair is None:
                pair = get_pair(act_dict['tokens'], word, i, 2, False, plase='У другому реченні')
        if pair:
            if (pair[0] in [p[1] for p in act_pairs]):
                # Помилка, коли лише число
                sys.exit("Помилка! Біля числа " + word['lemma'] + ' немає об\'єкта. У першому реченні')
            act_pairs.append([i] + pair)
    # обробка виключень
    for i in range(len(act_pairs)):
        if act_pairs[i][1] == 'мандарина':
            act_pairs[i][1] = 'мандарин'
        if act_pairs[i][-1] == 'и':
            act_pairs[i] = act_pairs[i][:-1]
        if len(act_pairs[i]) == 4 and act_pairs[i][1] == 'мандарин':
            act_pairs[i] = act_pairs[i][:3]

    # Визначення які об'єкти зменьшились/збільшились
    start = 0
    arr = sorted(neg_acts + pos_acts) + [len(act_dict['tokens'])]
    for i in range(1, len(arr)):
        tmp = [ii for ii, p in enumerate(act_pairs) if start < p[0] < arr[i]]
        # Якщо дія вказана без об'єктів - помилка
        if not tmp:
            sys.exit("Помилка! Дія '" + act_dict['tokens'][arr[i - 1]]['word'] + "' без участі предметів.")
        for j in tmp:
            if arr[i - 1] in neg_acts:
                # Якщо забрали фрукт, якого спочатку не було - помилка
                if act_pairs[j][1] not in [ii[1] for ii in table_pairs]:
                    sys.exit("Помилка! Фрукт: " + act_pairs[j][1] +
                             ' не було на столі спочатку - його не можна забрати.')
                act_pairs[j][2] = - act_pairs[j][2]
        start = arr[i]
    # print(act_pairs)

    # Масив дляереження результатів дій хлопчика
    new_pairs = [i[1:] for i in table_pairs]
    for i in act_pairs:
        if i[1] in [ii[1] for ii in table_pairs]:
            new_pairs[[ii[0] for ii in new_pairs].index(i[1])][1] += i[2]
            #  Помилка якщо зменьшено об'єкту більше аніж його було спершу
            if new_pairs[[ii[0] for ii in new_pairs].index(i[1])][1] < 0:
                sys.exit("Помилка! Неможливо від " + str(table_pairs[[ii[1] for ii in table_pairs].index(i[1])][2]) +
                         ' відняти ' + str(abs(i[2])) + ', бо буде від\'ємне число. Фрукт: ' + i[1])
        else:
            new_pairs.append(i[1:])
    # print(new_pairs)

    # Блок обробки запитань
    question = input('Введіть запитання.\n')
    while 'END' not in question:
        # Обробка запитання з запереченням поки не реалізовано
        if ' не ' in question:
            sys.exit("Помилка! Питання з 'не' виконатися не можуть.")
        # За відсутності слова "Скільки" - помилка
        if 'Скільки' not in question:
            sys.exit("Помилка! Питання не починаються зі слова 'Скільки'.")

        q_dict = nlp.extract_entities(question)
        # Пошук дій у запитанні, якщо іх немає - вважається, що потрібно вказати результат після виконання дій хлопчика
        # Важжається, що запитується тільки про одну з дій
        acts_q_an = [[word['lemma'], word['word']] for word in q_dict['tokens'] if word['lemma'] in acts_lemmas_n +
                     acts_lemmas_p]
        if len(acts_q_an) == 1:
            acts_q = acts_q_an[0][0]
            act_q_answer = acts_q_an[0][1]
        elif len(acts_q_an) > 1:
            sys.exit("Помилка! У запитані вказано більше однієї дії")
        else:
            acts_q = ""
            act_q_answer = ""
        # Отримання данних для обробки запитання з речення про дії хлопчика
        acts_for_q = [[i, word['lemma']] for i, word in enumerate(act_dict['tokens']) if word['lemma'] in acts_lemmas_n
                      + acts_lemmas_p]
        act_index_q = [0, len(act_dict['tokens'])]
        for i in range(len(acts_for_q)):
            if acts_for_q[i][1] == acts_q:
                act_index_q[0] = acts_for_q[i][0]
                if i != len(acts_for_q) - 1:
                    act_index_q[1] = acts_for_q[i+1][0]

        # Фрукти, що вказані в запитанні
        fruit_q = [fr for fr in q_dict['tokens'] if fr['lemma'] in fruits_lemmas]
        for i in range(len(fruit_q)):
            if fruit_q[i]['lemma'] == 'мандарина':
                fruit_q[i]['lemma'] = 'мандарин'
            if fruit_q[i]['lemma'][-1] == 'и':
                fruit_q[i]['lemma'] = fruit_q[i][:-1]

        # Фрукти, що вказані в запитані, але відсутні на столі
        fruit_q_not = [j['word'] for j in fruit_q if j['lemma'] not in [i[0] for i in new_pairs]]
        # Поведінка системи, залежно від запитання
        if fruit_q:  # Якщо вказано перелік фруктів
            if not acts_q:  # Для кількості фруктів, що брали участь у дії
                answer = sum([i[1] for i in new_pairs if i[0] in [j['lemma'] for j in fruit_q]])
            else:  # Лише для кількості фруктів після дій
                answer = sum([abs(i[2]) for i in act_pairs if
                              i[1] in [j['lemma'] for j in fruit_q] and (act_index_q[0] < i[0] < act_index_q[1])])
        elif 'фрукт' in [fr['lemma'] for fr in q_dict['tokens']]:  # Якщо вказано слово "фрукти" у запитанні
            if not acts_q:
                answer = sum([i[1] for i in new_pairs if len(i) != 3])
            else:
                answer = sum([abs(i[2]) for i in act_pairs if len(i) != 4 and (act_index_q[0] < i[0] < act_index_q[1])])
            fruit_q = [{'word': 'фруктів'}]
        else:  # Помила, якщо нічого не вказано
            sys.exit("Помилка! Питання не має слова 'фруки' або їх переліку.")

        # Вивід
        # Для об'єктів, яких не було на столі
        fruit_q_not_str = '' if not fruit_q_not else '; ' + ', '.join(fruit_q_not) + ' не було на столі спочатку'
        if not acts_q:  # Без дії
            print('Залишилось ' + str(answer) + ' ' +
                  ', '.join([j['word'] for j in fruit_q if j['word'] not in fruit_q_not]) + fruit_q_not_str)
        else:  # З дією
            # Для фруктів, про дію яких питається, але їх не чіпав хлопчик
            fruit_q_not_act = [j[1] for j in [[word['lemma'], word['word']] for word in q_dict['tokens']]
                               if j[0] in [i[1] for i in act_pairs if not (act_index_q[0] < i[0] < act_index_q[1])]]
            fruit_q_not_act_str = '.' if not fruit_q_not_act else '; ' + ', '.join(fruit_q_not_act) +\
                                                                  ' хлопчик не ' + act_q_answer
            print('Хлопчик ' + act_q_answer + ' ' + str(answer) + ' ' + ', '.join(
                [j['word'] for j in fruit_q if j['word'] not in fruit_q_not]) + fruit_q_not_str + fruit_q_not_act_str)

        # Нове запитання або кінець виконання
        question = input('Введіть нове запитання. Для завершення вводу запитань введіть END \n')
