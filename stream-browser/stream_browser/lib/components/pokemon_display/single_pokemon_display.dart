import 'package:flutter/material.dart';

import '../../constants/app_styles.dart';
import '../../models/pokemon.model.dart';
import '../../widgets/spacing.dart';
import 'encounter_timer.dart';
import 'pokemon_gif_image.dart';

class SinglePokemonDisplay extends StatelessWidget {
  const SinglePokemonDisplay({required this.pokemon, super.key});

  final PokemonModel pokemon;
  int get currentEnc => pokemon.encounters;
  String get shinyCounts =>
      '${pokemon.catches?.length ?? 0}/${pokemon.targets}';
  int? get startTime => pokemon.startedHuntTimestamp?.toInt();
  bool get smallText => '${pokemon.encounters}'.length > 4;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final double availableWidth = constraints.maxWidth;
        final maxCharsAllowed = availableWidth < 280 ? 4 : 5;
        final bool smallText = '${pokemon.encounters}'.length > maxCharsAllowed;

        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            PokemonGifImage(
              width: 100,
              height: 100,
              gifUrl: pokemon.gifUrl,
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
                        style: AppTextStyles.pokePixel(
                          fontSize: smallText ? 48 : 60,
                        ),
                      ),
                      Spacer(),
                      Text(
                        shinyCounts,
                        style: AppTextStyles.pokePixel(
                          fontSize: smallText ? 32 : 40,
                        ),
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
      },
    );
  }
}
