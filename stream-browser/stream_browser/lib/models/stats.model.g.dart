// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stats.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StatsModel _$StatsModelFromJson(Map<String, dynamic> json) => StatsModel(
      totalEggShinies: (json['totalEggShinies'] as num?)?.toInt() ?? 0,
      totalEggs: (json['totalEggs'] as num?)?.toInt() ?? 0,
      averageEggs: (json['averageEggs'] as num?)?.toDouble() ?? 0,
      totalStaticShinies: (json['totalStaticShinies'] as num?)?.toInt() ?? 0,
      totalStatic: (json['totalStatic'] as num?)?.toInt() ?? 0,
      averageStatic: (json['averageStatic'] as num?)?.toDouble() ?? 0,
      totalWildShinies: (json['totalWildShinies'] as num?)?.toInt() ?? 0,
      totalWild: (json['totalWild'] as num?)?.toInt() ?? 0,
      averageWild: (json['averageWild'] as num?)?.toDouble() ?? 0,
    );

Map<String, dynamic> _$StatsModelToJson(StatsModel instance) =>
    <String, dynamic>{
      'totalEggShinies': instance.totalEggShinies,
      'totalEggs': instance.totalEggs,
      'averageEggs': instance.averageEggs,
      'totalStaticShinies': instance.totalStaticShinies,
      'totalStatic': instance.totalStatic,
      'averageStatic': instance.averageStatic,
      'totalWildShinies': instance.totalWildShinies,
      'totalWild': instance.totalWild,
      'averageWild': instance.averageWild,
    };
