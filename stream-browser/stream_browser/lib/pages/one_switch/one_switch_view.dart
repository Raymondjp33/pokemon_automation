import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../constants/app_assets.dart';
import '../../models/pokemon.model.dart';
import '../../services/file_provider.dart';
import '../../widgets/scrolling_widget.dart';
import '../two_switch/components/switch_content.dart';

BorderSide containerBoarder({width = 5}) => BorderSide(
      color: Color(0xFF4C6CBF),
      width: width,
    );

class OneSwitchView extends StatelessWidget {
  const OneSwitchView({super.key});

  @override
  Widget build(BuildContext context) {
    String screen2Content =
        context.select((FileProvider state) => state.switch2Content);
    String game2Name =
        context.select((FileProvider state) => state.switch2Game);
    List<PokemonModel> pokemon2 =
        context.select((FileProvider state) => state.switch2Pokemon);

    return Scaffold(
      body: Container(
        width: 1280,
        height: 720,
        decoration: BoxDecoration(),
        child: Center(
          child: Stack(
            children: [
              ScrollingWidget(
                child: Image.asset(
                  AppAssets.oneSwitchBackground, fit: BoxFit.contain,
                  width: 1280,
                  height: 720,
                  // Capture the width only once to help calculate looping
                  // (assumes full screen width for background tile)
                  key: UniqueKey(), // prevents Flutter from recycling
                ),
              ),
              Positioned(
                child: Container(
                  width: 832,
                  height: 476,
                  decoration: BoxDecoration(
                    color: Colors.black,
                    border: Border.fromBorderSide(
                      containerBoarder(),
                    ),
                  ),
                ),
              ),
              Positioned(
                right: 0,
                child: Container(
                  width: 448,
                  height: 476,
                  padding: EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.6),
                    border: Border(
                      right: containerBoarder(),
                      top: containerBoarder(),
                      bottom: containerBoarder(),
                    ),
                  ),
                  child: Align(
                    alignment: Alignment.center,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SwitchContent(
                          screenContent: screen2Content,
                          gameName: game2Name,
                          pokemon: pokemon2,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
