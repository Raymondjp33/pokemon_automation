import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'pages/control_panel/control_panel_state.dart';
import 'pages/stats/stats_state.dart';

class NavKeyService {
  static GlobalKey<NavigatorState> globalNavigationKey =
      GlobalKey<NavigatorState>();
}

enum ERoute {
  controlPanel(name: 'controlPanel', path: '/'),
  stats(name: 'stats', path: '/stats');

  final String name;
  final String path;
  const ERoute({required this.name, required this.path});
}

final GoRouter router = GoRouter(
  navigatorKey: NavKeyService.globalNavigationKey,
  initialLocation: ERoute.controlPanel.path,
  restorationScopeId: 'router',
  routes: <RouteBase>[
    GoRoute(
      name: ERoute.controlPanel.name,
      path: ERoute.controlPanel.path,
      builder: (BuildContext context, GoRouterState state) {
        return ControlPanel();
      },
    ),
    GoRoute(
      name: ERoute.stats.name,
      path: ERoute.stats.path,
      builder: (BuildContext context, GoRouterState state) {
        return Stats();
      },
    ),
  ],
);
