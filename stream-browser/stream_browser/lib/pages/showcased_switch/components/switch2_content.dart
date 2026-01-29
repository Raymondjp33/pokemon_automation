import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../components/pokemon_display/pokemon_gif_image.dart';
import '../../../constants/app_styles.dart';
import '../../../models/pokemon.model.dart';
import '../../../services/file_provider.dart';
import '../../../widgets/spacing.dart';
import '../../../components/pokemon_display/encounter_timer.dart';

class Switch2Content extends StatelessWidget {
  const Switch2Content({super.key});

  @override
  Widget build(BuildContext context) {
    final List<PokemonModel>? pokemon =
        context.select((FileProvider e) => e.switch2Pokemon);

    int currentEncounters = pokemon?.firstOrNull?.encounters ?? 0;
    String shinyCounts =
        '${pokemon?.firstOrNull?.catches?.length ?? 0}/${pokemon?.firstOrNull?.targets ?? 0}';
    int? startTime = pokemon?.firstOrNull?.startedHuntTimestamp?.toInt();

    return Row(
      children: [
        PokemonGifImage(
          gifUrl: pokemon?.first.gifUrl ?? '',
          width: 120,
          height: 108,
        ),
        HorizontalSpace(10),
        Flexible(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Row(
                children: [
                  Text(
                    '$currentEncounters',
                    style: AppTextStyles.pokePixel(fontSize: 52),
                  ),
                  HorizontalSpace(30),
                  Text(
                    shinyCounts,
                    style: AppTextStyles.pokePixel(fontSize: 32),
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
