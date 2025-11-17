#!/usr/bin/env python3
"""
Generate combined modulation progressions by chaining two compatible progressions.
Reads modulationDB.json and creates an expanded version with combined progressions.
"""

import json
import copy
from pathlib import Path


def load_modulations(file_path):
    """Load the modulation database from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_modulations(modulations, file_path):
    """Save the modulation database to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(modulations, f, indent=4, ensure_ascii=False)


def are_compatible(prog1, prog2):
    """Check if two progressions can be chained together."""
    return prog1['to_mode'] == prog2['from_mode']


def combine_progressions(prog1, prog2, new_id):
    """
    Combine two progressions into a new one.

    Args:
        prog1: First progression
        prog2: Second progression
        new_id: ID for the new combined progression

    Returns:
        New combined progression
    """
    # Create the new progression structure
    new_progression = {
        'id': new_id,
        'modulation_technique': f"combo {prog1['modulation_technique']} {prog2['modulation_technique']}",
        'style': list(set(prog1['style'] + prog2['style'])),  # Merge and deduplicate styles
        'from_mode': prog1['from_mode'],
        'to_root': (prog1['to_root'] + prog2['to_root']) % 12,
        'to_mode': prog2['to_mode'],
        'chords': []
    }

    # Add chords from progression 1 (excluding the last chord which is a duplicate)
    for chord in prog1['chords'][:-1]:
        new_progression['chords'].append(copy.deepcopy(chord))

    # Add chords from progression 2 with offset applied to key_root
    offset = prog1['to_root']
    for chord in prog2['chords']:
        new_chord = copy.deepcopy(chord)
        new_chord['key_root'] = (new_chord['key_root'] + offset) % 12

        # Update comment to reflect the combination
        if 'comment' in new_chord:
            new_chord['comment'] = f"[from prog2] {new_chord['comment']}"

        new_progression['chords'].append(new_chord)

    return new_progression


def generate_combined_progressions(modulations):
    """
    Generate all valid combined progressions from existing ones.

    Args:
        modulations: List of existing progressions

    Returns:
        List of combined progressions
    """
    combined = []
    next_id = max(mod['id'] for mod in modulations) + 1

    # Try to combine each pair of progressions
    for i, prog1 in enumerate(modulations):
        for j, prog2 in enumerate(modulations):
            # Check if they can be chained
            if are_compatible(prog1, prog2):
                combined_prog = combine_progressions(prog1, prog2, next_id)
                combined.append(combined_prog)
                next_id += 1

                print(f"Combined progression {prog1['id']} -> {prog2['id']} (new ID: {combined_prog['id']})")
                print(f"  {prog1['from_mode']} -> {prog1['to_mode']} (root +{prog1['to_root']}) "
                      f"+ {prog2['from_mode']} -> {prog2['to_mode']} (root +{prog2['to_root']})")
                print(f"  = {combined_prog['from_mode']} -> {combined_prog['to_mode']} (root +{combined_prog['to_root']})")
                print(f"  Chords: {len(prog1['chords'])} + {len(prog2['chords'])} - 1 = {len(combined_prog['chords'])}")
                print()

    return combined


def main():
    """Main function to generate combined progressions."""
    input_file = Path('modulationDB.json')
    output_file = Path('modulationDB_expanded.json')

    print(f"Loading modulations from {input_file}...")
    modulations = load_modulations(input_file)
    original_count = len(modulations)
    print(f"Loaded {original_count} progressions\n")

    print("Generating combined progressions...")
    print("=" * 80)
    combined = generate_combined_progressions(modulations)
    print("=" * 80)
    print(f"\nGenerated {len(combined)} new combined progressions")

    # Add combined progressions to the original list
    expanded_modulations = modulations + combined
    total_count = len(expanded_modulations)

    print(f"\nTotal progressions: {total_count} (original: {original_count}, new: {len(combined)})")

    # Save the expanded database
    print(f"\nSaving expanded database to {output_file}...")
    save_modulations(expanded_modulations, output_file)
    print("Done!")

    # Print some statistics
    print("\n" + "=" * 80)
    print("Statistics:")
    print(f"  Original progressions: {original_count}")
    print(f"  Combined progressions: {len(combined)}")
    print(f"  Total progressions: {total_count}")
    print(f"  Growth factor: {total_count / original_count:.2f}x")


if __name__ == '__main__':
    main()
