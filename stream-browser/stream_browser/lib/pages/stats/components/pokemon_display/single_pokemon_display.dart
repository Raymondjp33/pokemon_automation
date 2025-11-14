import 'package:flutter/material.dart';
import 'package:gif/gif.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import '../../../../widgets/spacing.dart';
import '../encounter_timer.dart';

class SinglePokemonDisplay extends StatelessWidget {
  const SinglePokemonDisplay({required this.pokemon, super.key});

  final PokemonModel pokemon;
  int get currentEnc => pokemon.encounters;
  String get pokemonGifNumber => '${pokemon.gifNumber}';
  String get shinyCounts =>
      '${pokemon.catches?.length ?? 0}/${pokemon.targets}';
  int? get startTime => pokemon.startedHuntTimestamp?.toInt();

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 100,
          height: 100,
          child: Gif(
            image: NetworkImage(
              'https://raw.githubusercontent.com/adamsb0303/Shiny_Hunt_Tracker/master/Images/Sprites/3d/$pokemonGifNumber.gif',
            ),
            fit: BoxFit.contain,
            autostart: Autostart.loop,
          ),
        ),
        HorizontalSpace(10),
        Flexible(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    '$currentEnc',
                    style: AppTextStyles.pokePixel(fontSize: 60),
                  ),
                  HorizontalSpace(30),
                  Text(
                    shinyCounts,
                    style: AppTextStyles.pokePixel(fontSize: 40),
                  ),
                ],
              ),
              EncounterTimer(
                startTime: startTime,
                endTime: null,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
