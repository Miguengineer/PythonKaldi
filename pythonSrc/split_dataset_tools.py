def get_event_counts(data):
    event_counts = {}
    total_events = 0
    for utt_key in data.keys():
        events = data[utt_key].events
        total_events += len([event for event in events if event != "SIL"])
        for event in events:
            if event not in event_counts.keys():
                event_counts[event] = 1
            else:
                event_counts[event] += 1
    return event_counts


def fitness(train_idxs, test_idxs, all_data):
    from numpy import mean
    current_train_data = {}
    current_test_data = {}
    for key in train_idxs:
        current_train_data[key] = all_data.get_utt(key)
    for key in test_idxs:
        current_test_data[key] = all_data.get_utt(key)
    train_stats = get_event_counts(current_train_data)
    test_stats = get_event_counts(current_test_data)
    # Check that both train and test have the same key. If not, set count to 0
    for key in train_stats.keys():
        if key not in test_stats.keys():
            test_stats[key] = 0
    for key in test_stats.keys():
        if key not in train_stats.keys():
            train_stats[key] = 0

    total_events_train = 0
    for _, count in train_stats.items():
        total_events_train += count
    total_events_test = 0
    for _, count in test_stats.items():
        total_events_test += count
    # Test/train relative percentages
    train_relative_per = {}
    test_relative_per = {}
    for key in train_stats:
        train_relative_per[key] = 100.0 * train_stats[key] / total_events_train
        test_relative_per[key] = 100.0 * test_stats[key] / total_events_test
    # Fitness is just a number, not necessary to index by key
    fitness_per_phone = []
    for key in train_relative_per:
        min_per = min(train_relative_per[key], test_relative_per[key])
        sum_per = train_relative_per[key] + test_relative_per[key]
        fitness_per_phone.append(2 * min_per / sum_per * 100)
    return mean(fitness_per_phone)


def get_n_best(train_props, test_props, all_data, n):
    if len(train_props) != len(test_props):
        print("Error! Train and Test propositions have different number of elements!")
        return
    fitnesses = []
    for i in range(len(train_props)):
        current_train_prop = train_props[i]
        current_test_prop = test_props[i]
        fitnesses.append(fitness(current_train_prop, current_test_prop, all_data))
    sorted_idxs = sorted(range(len(fitnesses)), key=lambda k: fitnesses[k], reverse=True)
    new_train_props = []
    new_test_props = []
    # Keep only the first n idxs
    for i in range(n):
        new_train_props.append(train_props[sorted_idxs[i]])
        new_test_props.append(test_props[sorted_idxs[i]])
    return new_train_props, new_test_props


def mutation(first_idx_train, first_idx_test, n=2):
    from random import choice
    new_train = first_idx_train.copy()
    new_test = first_idx_test.copy()

    for i in range(n):
        # Interchange elements of train and test
        train_idx = choice(new_train)
        test_idx = choice(new_test)
        new_train.remove(train_idx)
        new_test.remove(test_idx)
        new_train.append(test_idx)
        new_test.append(train_idx)

    return new_train, new_test


def crossover(all_data, first_idx_train, second_idx_train):
    from utils import check_disjoint
    import numpy as np
    all_idxs = list(all_data.get_keys())
    # Keep only those idxs with no repeated utts
    new_train_idxs = list(np.unique(np.concatenate((first_idx_train, second_idx_train), axis=None)))
    np.random.shuffle(new_train_idxs)
    new_train_idxs = new_train_idxs[0:len(first_idx_train)]
    # Add removed events to test sets
    new_test_idxs = list(set(all_idxs) - set(new_train_idxs))
    if not check_disjoint(new_train_idxs, new_test_idxs):
        print("An error has occurred in crossover. train and test have coincidences?")
    return new_train_idxs, new_test_idxs


def run_epoch(train_idxs, test_idxs, all_data, win_per, cross_per, mut_per, test_per):
    from sklearn.model_selection import train_test_split
    n_best_prop = round(len(train_idxs) * win_per / 100)
    n_best_train_idxs, n_best_test_idxs = get_n_best(train_idxs, test_idxs, all_data, n_best_prop)

    n_cross = round(len(train_idxs) * cross_per / 100)
    for cross_idx in range(n_cross):
        train_cross, test_cross = crossover(all_data, train_idxs[0], train_idxs[1])
        n_best_train_idxs.append(train_cross)
        n_best_test_idxs.append(test_cross)
    n_mut = round(len(train_idxs) * mut_per / 100)
    for mut_idx in range(n_mut):
        train_mut, test_mut = mutation(train_idxs[0], test_idxs[0])
        n_best_train_idxs.append(train_mut)
        n_best_test_idxs.append(test_mut)
    n_difference = len(train_idxs) - len(n_best_train_idxs)
    for dif in range(n_difference):
        key_train, key_test = train_test_split(list(all_data.get_keys()), test_size=test_per / 100)
        n_best_train_idxs.append(key_train)
        n_best_test_idxs.append(key_test)

    return n_best_train_idxs, n_best_test_idxs


def train_test_dev_split(data, test_per=40, n_examples=500, win_per=25, mut_per=55, cross_per=5, max_epoch=150,
                         th_fit=99):
    from sklearn.model_selection import train_test_split
    num_utt = len(data.get_keys())
    print("Found " + str(num_utt) + " training examples (utterances)")
    print("Train set will contain " + str(100 - test_per) + "% of the examples")
    all_data_keys = list(data.get_keys())
    division_props_train = []
    division_props_test = []
    for n in range(n_examples):
        key_train, key_test = train_test_split(all_data_keys, test_size=test_per / 100)
        division_props_train.append(key_train)
        division_props_test.append(key_test)
    for epoch in range(max_epoch):
        print("Running epoch " + str(epoch) + ". Current fitness is " + str(
            fitness(division_props_train[0], division_props_test[0], data)))
        current_fit = fitness(division_props_train[0], division_props_test[0], data)
        if current_fit > th_fit:
            print("Fitness target reached at epoch " + str(epoch))
            break
        division_props_train, division_props_test = run_epoch(division_props_train, division_props_test,
                                                              data, win_per, cross_per, mut_per, test_per)

    print("Done!")
    return division_props_train[0], division_props_test[0]
