import 'package:flutter/material.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import '../../../../components/pokemon_display/unown_display.dart';
import '../../../components/pokemon_display/da_display.dart';
import '../../../models/display_content.model.dart';
import 'main_stats_display.dart';

class SwitchContent extends StatelessWidget {
  const SwitchContent({
    required this.screenContent,
    required this.pokemon,
    this.includeTitle = true,
    this.includeAverage = true,
    super.key,
  });

  final DisplayContent? screenContent;
  final List<PokemonModel> pokemon;
  final bool includeTitle;
  final bool includeAverage;

  @override
  Widget build(BuildContext context) {
    Widget child;
    switch (screenContent?.huntType ?? '') {
      case 'unown':
        child = UnownDisplay(
          key: ValueKey(screenContent),
          pokemon: pokemon,
        );
        break;

      case 'da':
        child = DaDisplay(
          key: ValueKey(screenContent),
          pokemon: pokemon,
        );
        break;

      case 'egg':
      case 'static':
      case 'wild':
      case 'oldwild':
      case 'current':
      default:
        child = MainStatsDisplay(
          key: ValueKey(screenContent),
          pokemon: pokemon,
          screenContent: screenContent,
          includeAverage: includeAverage,
        );
        break;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (includeTitle)
          Text(
            screenContent?.game ?? '',
            style: AppTextStyles.minecraftTen(fontSize: 36),
          ),
        Expanded(
          child: AnimatedSwitcher(
            duration: Duration(milliseconds: 700),
            transitionBuilder: (Widget child, Animation<double> animation) {
              return FadeTransition(
                opacity: animation,
                child: child,
              );
            },
            child: child,
          ),
        ),
      ],
    );
  }
}
