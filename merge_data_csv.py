import csv


def merge_csv(numbers, merged_filepath,  individual='simulations_run/independent/data{id}.csv'):
    with open(merged_filepath, 'w', newline='') as f:
        # using csv.writer method from CSV package
        f.write('Height, Velocity, Power\n')
        writer = csv.DictWriter(f, ['Height', 'Velocity', 'Power'])
        for number in numbers:
            with open(individual.format(id=number), 'r') as one_run:
                reader = csv.DictReader(one_run)
                rows = []
                for row in reader:
                    rows.append(row)
                writer.writerows(rows)

# returns merges 1, 2
# merge_csv(range(1, 3), 'simulations_run/merged_1_to_2.csv')






