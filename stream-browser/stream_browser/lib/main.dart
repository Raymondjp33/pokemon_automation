import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'pages/stats/components/left_block_content/left_switch_content.dart';
import 'pages/stats/components/middle_content.dart';
import 'pages/stats/components/right_block_content/right_switch_content.dart';
import 'services/file_provider.dart';
import 'widgets/scrolling_background.dart';

void main() {
  runApp(const App());
}

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => FileProvider(),
          lazy: false,
        ),
      ],
      child: MaterialApp(
        title: 'Stream Browser',
        theme: ThemeData(
          useMaterial3: true,
        ),
        home: const Home(),
      ),
    );
  }
}

class Home extends StatelessWidget {
  const Home({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Stack(
          children: [
            Container(
              width: 1280,
              height: 354,
              child: InfiniteScrollBackground(),
            ),
            Container(
              width: 1280,
              height: 354,
              child: Row(
                children: [
                  Container(
                    width: 427,
                    height: 354,
                    padding: EdgeInsets.symmetric(vertical: 10, horizontal: 20),
                    decoration: const BoxDecoration(
                      border: Border(
                        right: BorderSide(width: 5, color: Color(0xFF4C6CBF)),
                      ),
                    ),
                    child: LeftSwitchContent(),
                  ),
                  Container(
                    width: 426,
                    height: 354,
                    padding: EdgeInsets.symmetric(vertical: 10, horizontal: 2),
                    child: MiddleContent(),
                  ),
                  Container(
                    width: 427,
                    height: 354,
                    padding: EdgeInsets.symmetric(vertical: 10, horizontal: 20),
                    decoration: const BoxDecoration(
                      border: Border(
                        left: BorderSide(width: 5, color: Color(0xFF4C6CBF)),
                      ),
                    ),
                    child: RightSwitchContent(),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
