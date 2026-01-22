import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import '../../../../services/file_provider.dart';
import '../main_stats_display.dart';

class RightSwitchContent extends StatelessWidget {
  const RightSwitchContent({super.key});

  @override
  Widget build(BuildContext context) {
    String screenContent =
        context.select((FileProvider state) => state.switch2Content);
    String gameName = context.select((FileProvider state) => state.switch2Game);
    List<PokemonModel> pokemon =
        context.select((FileProvider state) => state.switch2Pokemon);

    Widget child;
    switch (screenContent) {
      case 'egg':
      case 'static':
      case 'wild':
      case 'current':
      default:
        child = MainStatsDisplay(
          key: ValueKey(screenContent),
          pokemon: pokemon,
          screenContent: screenContent,
        );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          gameName,
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
