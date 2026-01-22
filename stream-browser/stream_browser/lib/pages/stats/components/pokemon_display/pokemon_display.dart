import 'package:flutter/material.dart';

import '../../../../models/pokemon.model.dart';
import 'pokemon_row.dart';
import '../../../../widgets/scrolling_widget.dart';
import 'single_pokemon_display.dart';

class PokemonDisplay extends StatelessWidget {
  const PokemonDisplay({required this.pokemon, super.key});

  final List<PokemonModel> pokemon;

  @override
  Widget build(BuildContext context) {
    if (pokemon.isEmpty) {
      return Container();
    }

    if (pokemon.length == 1) {
      return SinglePokemonDisplay(pokemon: pokemon.first);
    }

    return Center(
      child: pokemon.length > 3
          ? Container(
              height: 139,
              child: ScrollingWidget(
                scrollSpeed: 30,
                child: PokemonRow(
                  targets: pokemon,
                  pokemonGifSize: 70,
                ),
              ),
            )
          : PokemonRow(
              targets: pokemon,
              pokemonGifSize: 90,
            ),
    );
  }
}
