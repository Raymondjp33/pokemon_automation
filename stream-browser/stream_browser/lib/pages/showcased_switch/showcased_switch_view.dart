import 'package:flutter/material.dart';

import '../../constants/app_assets.dart';
import '../../widgets/scrolling_widget.dart';
import 'components/switch1_content.dart';
import 'components/switch2_content.dart';

BorderSide containerBoarder({width = 5}) => BorderSide(
      color: Color(0xFF4C6CBF),
      width: width,
    );

class ShowcasedSwitchView extends StatelessWidget {
  const ShowcasedSwitchView({super.key});

  @override
  Widget build(BuildContext context) {
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
                  AppAssets.cloudBackgroundFullLight, fit: BoxFit.contain,
                  width: 1280,
                  height: 720,
                  // Capture the width only once to help calculate looping
                  // (assumes full screen width for background tile)
                  key: UniqueKey(), // prevents Flutter from recycling
                ),
              ),
              Positioned(
                right: 0,
                child: Container(
                  width: 325,
                  height: 720,
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.6),
                    border: Border(
                      left: containerBoarder(width: 3),
                    ),
                  ),
                  child: Column(
                    children: [
                      Container(
                        width: 325,
                        height: 186,
                        decoration: BoxDecoration(
                          color: Colors.black,
                          border: Border(
                            top: containerBoarder(),
                            bottom: containerBoarder(),
                            right: containerBoarder(),
                          ),
                        ),
                      ),
                      Container(
                        width: 325,
                        height: 174,
                        decoration: BoxDecoration(
                          border: Border(
                            right: containerBoarder(),
                          ),
                        ),
                        child: Switch1Content(),
                      ),
                      Container(
                        width: 325,
                        height: 186,
                        decoration: BoxDecoration(
                          color: Colors.black,
                          border: Border(
                            top: containerBoarder(),
                            bottom: containerBoarder(),
                            right: containerBoarder(),
                          ),
                        ),
                      ),
                      Container(
                        width: 325,
                        height: 174,
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: containerBoarder(),
                            right: containerBoarder(),
                          ),
                        ),
                        child: Switch2Content(),
                      ),
                    ],
                  ),
                ),
              ),
              Positioned(
                child: Container(
                  width: 955,
                  height: 546,
                  decoration: BoxDecoration(
                    color: Colors.black,
                    border: Border(
                      top: containerBoarder(),
                      bottom: containerBoarder(),
                      left: containerBoarder(),
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
