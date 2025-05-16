import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'router.dart';
import 'services/file_provider.dart';

class App extends StatefulWidget {
  const App({super.key});

  @override
  State<App> createState() => _AppState();
}

class _AppState extends State<App> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => FileProvider(),
          lazy: false,
        ),
      ],
      child: MaterialApp.router(
        theme: ThemeData(
          useMaterial3: true,
        ),
        routerConfig: router,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
